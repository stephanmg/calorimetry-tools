import pandas as pd

def collect_data(name="CO2", wt_file="UCP1_controls_CO2.csv", ko_file="UCP1_knockouts_CO2.csv", gene_symbol="Ucp1"):
    df_WT = pd.read_csv(wt_file)
    df_WT["gene_symbol"] = f"{gene_symbol} WT"

    df_KO = pd.read_csv(ko_file)
    df_KO["gene_symbol"] = f"{gene_symbol} KO"

    df_both = pd.concat([df_KO, df_WT])
    df_both = df_both[["external_sample_id", "data_point", "weight", "time_point", "discrete_point", "gene_symbol"]]
    df_both.rename(columns={"external_sample_id" : "Sample", "data_point": name, "weight": "Weight", "time_point": "DateTime", "discrete_point": "Time", "gene_symbol": "Condition"}, inplace=True)
    return df_both

def combine_measurements(df1, df2):
    df_combined = df_CO2.merge(df_O2, on=["DateTime", "Sample"], suffixes=('', '_drop'))
    df_combined = df_combined.loc[:, ~df_combined.columns.str.endswith('_drop')]
    return df_combined

if __name__ == "__main__":
    df_CO2 = collect_data()
    df_O2 = collect_data(name="O2", wt_file="UCP1_controls_O2.csv", ko_file="UCP1_knockouts_CO2.csv", gene_symbol="Ucp1")
    print(df_O2)
    df_all = combine_measurements(df_CO2, df_O2)
    print(df_all)
