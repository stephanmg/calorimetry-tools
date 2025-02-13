import pandas as pd


def convert_to_tse(df, gene_symbol, filename, use_selection_of_animals=True):
    df["Sample"] = df["Sample"].apply(lambda x: str(x).split("-")[-1] if "-" in str(x) else str(x))

    samples = list(set(df["Sample"]))
    boxes = [i for (i, j) in list(enumerate(samples))]
    animals = [j for (i, j) in list(enumerate(samples))]
    num_samples = len(boxes)

    unique_ids = df[['Sample', 'Condition', 'Weight', 'Sex']].astype(str).agg("_".join, axis=1)
    unique_ids = [(*uid.split("_"), index) for (index, uid) in enumerate(unique_ids.tolist())]

    ko = list(df.loc[df['Condition'].str.contains("KO", na=False), "Sample"])
    unique_kos = len(list(set(ko)))
    ko = list(set([f"{k}" for k in ko]))
    wt = list(df.loc[df['Condition'].str.contains("WT", na=False), "Sample"])[:unique_kos]
    wt = list(set([f"{w}" for w in wt]))

    selection_of_animal_ids = [sample[0] for sample in unique_ids]


    if use_selection_of_animals:
        selection_of_animal_ids = wt + ko
        filename_out = f"example_selection_{gene_symbol}.csv"

    with open(filename, "w") as f:
        f.write("20200508_SD_Ucpdd_K1;TX001;TX002;TX003;;;\n")
        f.write(";TSE LabMaster V6.3.3 (2017-3514);;;;;\n") 
        f.write("Box;Animal No.; Weight [g];Genotype;Sex;;\n")
        for animal_id in selection_of_animal_ids:
            for _, (animal, genotype, weight, sex, box) in enumerate(unique_ids):
                if animal_id == animal:
                    f.write(f"{box};{animal};{weight};{genotype};{sex};;\n")
                    break
        f.write(";;;;;;\n")
        f.write("Date;Time;Animal No.;Box;VO2(3);VCO2(3);WeightBody\n")
        f.write(";;;;[ml/h];[ml/h];[g]\n")
        for index, row in df.iterrows():
            animal = unique_ids[index][0]
            if animal in selection_of_animal_ids: 
                box = unique_ids[index][3]
                o2 = str(row['O2']).replace(".", ",")
                co2 = str(row['CO2']).replace(".", ",")
                date, time = row["DateTime"].split(" ")
                weight = str(row['Weight']).replace(".", ",")
                f.write(f"{date};{time};{row['Sample']};{box};{o2};{co2};{weight}\n")
                

if __name__ == "__main__":
    gene_symbol = "Adipoq"
    df = pd.read_csv(f"reformatted_calor_{gene_symbol}.csv")
    convert_to_tse(df, gene_symbol, "test_new2.csv")
