
import pandas as pd
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "2025"
SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "verification_vehicules"

SORTIE.mkdir(parents=True, exist_ok=True)

# Importation
vehicules = pd.read_csv(
    DATA_DIR / "vehicules-2025.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype="string"
)

usagers = pd.read_csv(
    DATA_DIR / "usagers-2025.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype="string"
)

# Nettoyage des espaces extérieurs
for df in [vehicules, usagers]:
    df.columns = df.columns.str.strip()

    for col in df.columns:
        df[col] = df[col].str.strip()

# Accidents à examiner
accidents = [
    "202500013215",
    "202500013431",
    "202500034910",
    "202500042211"
]

# Filtrer les deux tables
vehicules_selection = vehicules[
    vehicules["Num_Acc"].isin(accidents)
].copy()

usagers_selection = usagers[
    usagers["Num_Acc"].isin(accidents)
].copy()

print("\n========== VEHICULES REELS ==========")
print(vehicules_selection.to_string(index=False))

print("\n========== USAGERS REELS ==========")
print(usagers_selection.to_string(index=False))

# Export des résultats
vehicules_selection.to_csv(
    SORTIE / "vehicules_reels.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

usagers_selection.to_csv(
    SORTIE / "usagers_reels.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# Comparaison avec num_veh
print("\n========== COMPARAISON PAR NUM_VEH ==========")

comparaison = usagers_selection.merge(
    vehicules_selection,
    on=["Num_Acc", "num_veh"],
    how="outer",
    suffixes=("_usager", "_vehicule"),
    indicator=True
)

print(comparaison.to_string(index=False))

comparaison.to_csv(
    SORTIE / "comparaison_par_num_veh.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# Résumé par accident
print("\n========== RESUME PAR ACCIDENT ==========")

for num_acc in accidents:

    v = vehicules_selection[
        vehicules_selection["Num_Acc"] == num_acc
    ]

    u = usagers_selection[
        usagers_selection["Num_Acc"] == num_acc
    ]

    print(f"\nAccident : {num_acc}")
    print("Nombre de véhicules :", len(v))
    print("Nombre d'usagers :", len(u))

    print("Num_veh des véhicules :",
          v["num_veh"].dropna().unique().tolist())

    print("Num_veh des usagers :",
          u["num_veh"].dropna().unique().tolist())

print("\nAnalyse terminée.")
print("Résultats enregistrés dans :", SORTIE)
