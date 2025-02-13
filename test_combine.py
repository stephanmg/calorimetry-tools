import pandas as pd
import re

def map_to_calor(df):
    df.rename(columns={"Sample": "Animal No._NA", "CO2": "VCO2(3)_[ml/h]", "O2": "O2(3)_[ml/h]"}, inplace=True)
    return df

def format_datetime(df):
    df["DateTime"] = df["DateTime"].apply(lambda s: re.sub("(.*?)-(.*?)-(.*?)\s(.*?):(.*?):.*", r"\3/\2/\1 \4:\5", s))
    return df

def collect_data(name="CO2", wt_file="UCP1_controls_CO2.csv", ko_file="UCP1_knockouts_CO2.csv", gene_symbol="Ucp1"):
    df_WT = pd.read_csv(wt_file)
    df_WT["gene_symbol"] = f"{gene_symbol} WT"

    df_KO = pd.read_csv(ko_file)
    df_KO["gene_symbol"] = f"{gene_symbol} KO"

    df_both = pd.concat([df_KO, df_WT])
    df_both = df_both[["external_sample_id", "data_point", "weight", "time_point", "discrete_point", "gene_symbol", "sex"]]
    df_both.rename(columns={"external_sample_id" : "Sample", "data_point": name, "weight": "Weight", "time_point": "DateTime", "discrete_point": "Time", "gene_symbol": "Condition", "sex": "Sex"}, inplace=True)
    return df_both

def combine_measurements(df1, df2):
    df_combined = df_CO2.merge(df_O2, on=["DateTime", "Sample"], suffixes=('', '_drop'))
    df_combined = df_combined.loc[:, ~df_combined.columns.str.endswith('_drop')]
    return df_combined

if __name__ == "__main__":
    gene_symbol = "Ucp1"
    gene_symbol = "Adipoq"
    df_CO2 = collect_data(name="CO2", wt_file=f"{gene_symbol}_controls_CO2.csv", ko_file=f"{gene_symbol}_knockouts_CO2.csv", gene_symbol=gene_symbol)
    df_O2 = collect_data(name="O2", wt_file=f"{gene_symbol}_controls_O2.csv", ko_file=f"{gene_symbol}_knockouts_CO2.csv", gene_symbol=gene_symbol)
    df_all = combine_measurements(df_CO2, df_O2)
    df_reformatted = format_datetime(df_all)
    df_reformatted.to_csv(f"reformatted_calor_{gene_symbol}.csv")
