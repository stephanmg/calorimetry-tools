from impc_api import solr_request, batch_solr_request

import tempfile
import json
import os
from types import SimpleNamespace

def get_dataset_identifier(gene_symbol, to_find, significance):
    """ Receive an unique identifier for the dataset """

    # The returned fields (fl) in this Solr request do uniquely identify an experiment
    params = {
        'q': f'marker_symbol:{gene_symbol} AND procedure_name:"Indirect Calorimetry" AND parameter_name:"{to_find}" AND significant:{significance}',
        'fl': 'procedure_name,colony_id,parameter_name,metadata_group,id,doc_id,zygosity,parameter_stable_id,strain_name,production_center,pipeline_stable_id'
    }

    with tempfile.NamedTemporaryFile(mode="w+", delete=True) as tmp_file:
        temp_filename = tmp_file.name

    try:
        batch_solr_request(core='statistical-result', params=params, download=True, batch_size=100, filename=temp_filename)
        with open(f"{temp_filename}.json") as f:
            return json.load(f)
    finally:
        os.remove(f"{temp_filename}.json")


def get_measurement_for_dataset_with_identifiers(gene_symbol, to_find, biological_sample_group, filetype="csv", batch_size=10000, download=True):
    """ Retrieve measurement data (O2 or CO2) for a gene symbol and given biological sample group (KO or WT) """
    # Multiple statistical results might be available. The underlying experiment can be identified by any. Thus we can take 
    # the first statistical result available and assume we can construct an unique identifier by the selected return fields
    identifier = SimpleNamespace(**(get_dataset_identifier(gene_symbol, to_find, significance="False")[0]))

    assert len(get_dataset_identifier(gene_symbol, to_find, significance="False")) == 1, "Either no or too many experiments found"
    
    # Get shorter name for parameter for ouput to filename
    if to_find == "Carbon dioxide production":
        parameter_stable_id = "IMPC_CAL_004_001"
        parameter_name = "CO2"
    if to_find == "Oxygen consumption":
        parameter_stable_id = "IMPC_CAL_003_001"
        parameter_name = "O2"

    # Get full output filename
    if biological_sample_group == "experimental":
        filename = f"{gene_symbol}_knockouts_{parameter_name}"
    if biological_sample_group == "control":
        filename = f"{gene_symbol}_controls_{parameter_name}"
    
    # Create query parameters for Solr
    params={
        'q': f'parameter_name:"{to_find}" AND metadata_group:"{identifier.metadata_group}" AND zygosity: "{identifier.zygosity}" AND gene_symbol:"{gene_symbol}" AND parameter_stable_id:"{parameter_stable_id}" AND strain_name:"{identifier.strain_name}" AND biological_sample_group: "{biological_sample_group}"', 
        'fl': 'weight,file_type,data_point,external_sample_id,time_point,window_weight,discrete_point,strain_name,metadata_group,parameter_stable_id,gene_symbol,sex',
        'wt': filetype
    }

    # For WT negative selection (empty gene symbol, as we have no specific gene knocked out)
    if biological_sample_group == "control":
        params["q"] = params["q"].replace(f'gene_symbol:"{gene_symbol}"', r'-gene_symbol:*')
        print(params["q"])

    # Retrieve dataset, depending on size, the operation might take a while
    batch_solr_request(core='experiment', params=params, download=download, batch_size=batch_size, filename=filename)

def get_measurements_for_gene_symbol(gene_symbol, which="KO"):
    """ Get measurements for the gene symbol for KO or WT """
    if which in ["both", "KO"]:
        # KO
        get_measurement_for_dataset_with_identifiers(gene_symbol, "Carbon dioxide production", "experimental")
        get_measurement_for_dataset_with_identifiers(gene_symbol, "Oxygen consumption", "experimental")

    if which in ["both", "WT"]:
        # WT
        get_measurement_for_dataset_with_identifiers(gene_symbol, "Carbon dioxide production", "control")
        get_measurement_for_dataset_with_identifiers(gene_symbol, "Oxygen consumption", "control")


if __name__ == "__main__":
    # Ucp1
    get_measurements_for_gene_symbol("Ucp1")

    # Adipoq
    get_measurements_for_gene_symbol("Adipoq")
