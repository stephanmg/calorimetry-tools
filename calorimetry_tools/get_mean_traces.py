import pandas as pd


sexes = ["male", "female"]
conditions = ["WT", "KO"]
gene_symbol = "Ucp1"

for sex in sexes:
    pd_final = pd.DataFrame()
    for index, condition in enumerate(conditions):
        # Filter for condition and sex
        df = pd.read_csv("reformatted_calor_Ucp1_new.csv")

        df = df[df["Condition"] == f"{gene_symbol} {condition}"]
        df = df[df["Sex"] == sex]

        # calculate timebin because times are not necessarily aligned
        df["Timestamp"] = pd.to_datetime(df["DateTime"])
        df["StartTime"] = df.groupby("Sample")["Timestamp"].transform("min")
        df["TimeDelta"] = df["Timestamp"] - df["StartTime"]
        df["AlignedTime"] = pd.to_datetime("2000-01-01 18:00") + df["TimeDelta"]
        df["Timebin"] = df["AlignedTime"].dt.floor("10T")

        # old (not required)
        # df['RescaledTime'] = pd.to_datetime("2000-01-01") + df["Timedelta"]
        # df['Timebin'] = df["RescaledTime"].dt.floor('10T')
        # df['Timebin'] = df['Timestamp'].dt.floor('10T')

        # new (simpler bsaed on Time of one day)
        # df["TimeDelta"] = pd.to_timedelta(df["Time"], unit="h")
        ##df["Timebin"] =  pd.to_datetime("2000-01-01 18:00") + df["TimeDelta"]
        # df["Timebin"] =  df["TimeDelta"]

        print(df["Timebin"])

        # calculate mean traces
        mean_trace_O2 = df.groupby("Timebin")["O2"].mean().reset_index()
        # mean_trace_O2["O2"] = mean_trace_O2["O2"].rolling(window=3, min_periods=1).mean()
        mean_trace_CO2 = df.groupby("Timebin")["CO2"].mean().reset_index()
        mean_trace_weight = df.groupby("Timebin")["Weight"].mean().reset_index()
        mean_trace_time = df.groupby("Timebin")["Time"].mean().reset_index()
        print(mean_trace_time["Time"])

        # calculate back to time bin back to Datetime
        # mean_trace_O2["Timebin"] = mean_trace_O2["Timebin"].dt.strftime("%d/%m/%Y %H:%M")
        # mean_trace_CO2["Timebin"] = mean_trace_CO2["Timebin"].dt.strftime("%d/%m/%Y %H:%M")

        # final df
        df_final = pd.DataFrame(
            {
                "CO2": mean_trace_CO2["CO2"],
                "O2": mean_trace_O2["O2"],
                "DateTime": mean_trace_CO2["Timebin"],
                "Sample": index,
                "Sex": sex,
                "Condition": f"{gene_symbol} {condition}",
                "Weight": mean_trace_weight["Weight"],
                "RelativeTime": mean_trace_time["Time"],
            }
        )

        pd_final = pd.concat([pd_final, df_final])
    pd_final.to_csv(f"mean_traces_for_{gene_symbol}_{sex}.csv")

    import seaborn as sns
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 5))
    # sns.lineplot(data=pd_final, x="DateTime", y="O2", hue="Condition", marker="o")
    sns.lineplot(
        data=pd_final, x="RelativeTime", y="O2", hue="Condition", marker="o"
    )
    plt.savefig(f"test_fig_Ucp1_{condition}_{sex}.png", dpi=300)

    # ,Sample,CO2,Weight,DateTime,Time,Condition,Sex,O2
