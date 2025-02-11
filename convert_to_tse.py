import pandas as pd

df = pd.read_csv("reformatted_calor_Adipoq.csv")
#df["Sample"] = df["Sample"].str.extract(r'(\d+)$')[0]
df["Sample"] = df["Sample"].apply(lambda x: str(x).split("-")[-1] if "-" in str(x) else str(x))


samples = list(set(df["Sample"]))
boxes = [i for (i, j) in list(enumerate(samples))]
animals = [j for (i, j) in list(enumerate(samples))]
num_samples = len(boxes)

unique_ids = df[['Sample', 'Condition', 'Weight', 'Sex']].astype(str).agg("_".join, axis=1)
print(len(unique_ids))
unique_ids = [(*uid.split("_"), index) for (index, uid) in enumerate(unique_ids.tolist())]

# TODO: pick 10 or 12 ids from the df instead of manually picking
ko = [30332480, 30327906, 30327907, 30314498, 30300774, 30300775, 30322409, 30300777, 30300781, 30314512, 30332401, 30332410, 30332406, 30314490]
ko = list(df.loc[df['Condition'].str.contains("KO", na=False), "Sample"])
unique_kos = len(list(set(ko)))
ko = [f"{k}" for k in ko]
wt = [30310286, 30310287, 30310289, 30310290, 30310291, 30351248, 30326686, 30326687, 30326688, 30326699, 30326700, 30326701, 30326702, 30351279]
wt = list(df.loc[df['Condition'].str.contains("WT", na=False), "Sample"])[:unique_kos]
wt = [f"{w}" for w in wt]

wt = list(set(wt))
ko = list(set(ko))


#print(wt)
#print(ko)

use_selection_of_animals = True

selection_of_animal_ids = [sample[0] for sample in unique_ids]


filename_out = "example.csv"
if use_selection_of_animals:
    selection_of_animal_ids = wt + ko
    filename_out = "example_selection_Adipoq.csv"
print(selection_of_animal_ids)

with open(filename_out, "w") as f:
    # 5 semicolons so far - check
    f.write("20200508_SD_Ucpdd_K1;TX001;TX002;TX003;;\n")
    f.write(";TSE LabMaster V6.3.3 (2017-3514);;;;\n") 
    f.write("Box;Animal No.; Weight [g];Genotype;Sex;\n")
    for animal_id in selection_of_animal_ids:
        for _, (animal, genotype, weight, sex, box) in enumerate(unique_ids):
            if animal_id == animal:
                f.write(f"{box};{animal};{weight};{genotype};{sex};\n")
                break
    f.write(";;;;;\n")
    f.write("Date;Time;Animal No.;Box;VO2(3);VCO2(3)\n")
    f.write(";;;;[ml/h];[ml/h]\n")
    for index, row in df.iterrows():
        animal = unique_ids[index][0]
        if animal in selection_of_animal_ids: 
            box = unique_ids[index][3]
            o2 = str(row['O2']).replace(".", ",")
            co2 = str(row['CO2']).replace(".", ",")
            date, time = row["DateTime"].split(" ")
            f.write(f"{date};{time};{row['Sample']};{box};{o2};{co2}\n")
