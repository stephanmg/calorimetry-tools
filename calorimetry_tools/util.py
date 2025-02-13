""" Util """
import os
import re
import json
import tempfile
from types import SimpleNamespace

import pandas as pd
from impc_api import batch_solr_request


def map_to_calor(df):
    """Map columns of df to CALOR compatible column names"""
    df.rename(
        columns={
            "Sample": "Animal No._NA",
            "CO2": "VCO2(3)_[ml/h]",
            "O2": "O2(3)_[ml/h]",
        },
        inplace=True,
    )
    return df


def format_datetime(df):
    """Re-format DateTime from YYYY-MM-DD:HH:MM to TSE format DD/MM/YYYY HH:MM"""
    df["DateTime"] = df["DateTime"].apply(
        lambda s: re.sub(
            r"(.*?)-(.*?)-(.*?)\s(.*?):(.*?):.*", r"\3/\2/\1 \4:\5", s
        )
    )
    return df


def collect_data(name, wt_file, ko_file, gene_symbol):
    """Collect measurement data from files"""
    df_wt = pd.read_csv(wt_file)
    df_wt["gene_symbol"] = f"{gene_symbol} WT"

    df_ko = pd.read_csv(ko_file)
    df_ko["gene_symbol"] = f"{gene_symbol} KO"

    df_both = pd.concat([df_ko, df_wt])
    df_both = df_both[
        [
            "external_sample_id",
            "data_point",
            "weight",
            "time_point",
            "discrete_point",
            "gene_symbol",
            "sex",
        ]
    ]
    df_both.rename(
        columns={
            "external_sample_id": "Sample",
            "data_point": name,
            "weight": "Weight",
            "time_point": "DateTime",
            "discrete_point": "Time",
            "gene_symbol": "Condition",
            "sex": "Sex",
        },
        inplace=True,
    )
    return df_both


def combine_measurements(df_co2, df_o2):
    """Combine multiple measurements"""
    df_combined = df_co2.merge(
        df_o2, on=["DateTime", "Sample"], suffixes=("", "_drop")
    )
    df_combined = df_combined.loc[:, ~df_combined.columns.str.endswith("_drop")]
    return df_combined


def combine_measurements_for_gene_symbol(gene_symbol, base_folder="results/"):
    """Finally combine the data frames"""
    df_co2 = collect_data(
        name="CO2",
        wt_file=f"{base_folder}/{gene_symbol}_controls_CO2.csv",
        ko_file=f"{base_folder}/{gene_symbol}_knockouts_CO2.csv",
        gene_symbol=gene_symbol,
    )
    df_o2 = collect_data(
        name="O2",
        wt_file=f"{base_folder}/{gene_symbol}_controls_O2.csv",
        ko_file=f"{base_folder}/{gene_symbol}_knockouts_CO2.csv",
        gene_symbol=gene_symbol,
    )
    df_all = combine_measurements(df_co2, df_o2)
    df_reformatted = format_datetime(df_all)
    return df_reformatted


def get_dataset_identifier(gene_symbol, to_find, significance):
    """Receive an unique identifier for the dataset"""

    # The returned fields (fl) in this Solr request do uniquely identify an experiment
    params = {
        "q": f'marker_symbol:{gene_symbol} AND procedure_name:"Indirect Calorimetry" AND parameter_name:"{to_find}" AND significant:{significance}',  # pylint: disable=C0301
        "fl": "procedure_name,colony_id,parameter_name,metadata_group,id,doc_id,zygosity,parameter_stable_id,strain_name,production_center,pipeline_stable_id",  # pylint: disable=C0301
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp_file:
        temp_filename = tmp_file.name

    try:
        batch_solr_request(
            core="statistical-result",
            params=params,
            download=True,
            batch_size=100,
            filename=temp_filename,
        )
        with open(f"{temp_filename}.json") as f:
            return json.load(f)
    finally:
        os.remove(f"{temp_filename}.json")


def get_measurement_for_dataset_with_identifiers(
    gene_symbol,
    to_find,
    biological_sample_group,
    output_folder="results/",
    filetype="csv",
    batch_size=10000,
    download=True,
):
    """Retrieve measurement data (O2 or CO2) for a gene symbol and given
    biological sample group (KO or WT)"""
    # Multiple statistical results might be available. The underlying experiment
    # can be identified by any. Thus we can take the first statistical result
    # available and assume we can construct an unique identifier by the selected
    # return fields
    identifier = SimpleNamespace(
        **(
            get_dataset_identifier(gene_symbol, to_find, significance="False")[
                0
            ]
        )
    )

    # Consistency check
    assert (
        len(get_dataset_identifier(gene_symbol, to_find, significance="False"))
        == 1
    ), "Either no or too many experiments found"

    # Get shorter name for parameter for ouput to filename
    parameter_name = ""
    parameter_stable_id = ""
    if to_find == "Carbon dioxide production":
        parameter_stable_id = "IMPC_CAL_004_001"
        parameter_name = "CO2"
    if to_find == "Oxygen consumption":
        parameter_stable_id = "IMPC_CAL_003_001"
        parameter_name = "O2"

    # Get full output filename
    filename = ""
    if biological_sample_group == "experimental":
        filename = f"{output_folder}/{gene_symbol}_knockouts_{parameter_name}"
    if biological_sample_group == "control":
        filename = f"{output_folder}/{gene_symbol}_controls_{parameter_name}"

    # Create query parameters for Solr
    params = {
        "q": f'parameter_name:"{to_find}" AND metadata_group:"{identifier.metadata_group}" AND zygosity: "{identifier.zygosity}" AND gene_symbol:"{gene_symbol}" AND parameter_stable_id:"{parameter_stable_id}" AND strain_name:"{identifier.strain_name}" AND biological_sample_group: "{biological_sample_group}"',  # pylint: disable=C0301
        "fl": "weight,file_type,data_point,external_sample_id,time_point,window_weight,discrete_point,strain_name,metadata_group,parameter_stable_id,gene_symbol,sex",  # pylint: disable=C0301
        "wt": filetype,
    }

    # For WT negative selection (empty gene symbol, as we have no specific gene knocked out)
    if biological_sample_group == "control":
        params["q"] = params["q"].replace(
            f'gene_symbol:"{gene_symbol}"', r"-gene_symbol:*"
        )

    # Retrieve dataset, depending on size, the operation might take a while
    batch_solr_request(
        core="experiment",
        params=params,
        download=download,
        batch_size=batch_size,
        filename=filename,
    )


def get_measurements_for_gene_symbol(gene_symbol, which="KO"):
    """Get measurements for the gene symbol for KO or WT"""
    if which in ["both", "KO"]:
        # KO
        get_measurement_for_dataset_with_identifiers(
            gene_symbol, "Carbon dioxide production", "experimental"
        )
        get_measurement_for_dataset_with_identifiers(
            gene_symbol, "Oxygen consumption", "experimental"
        )

    if which in ["both", "WT"]:
        # WT
        get_measurement_for_dataset_with_identifiers(
            gene_symbol, "Carbon dioxide production", "control"
        )
        get_measurement_for_dataset_with_identifiers(
            gene_symbol, "Oxygen consumption", "control"
        )
