
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DOSSIER = BASE_DIR / "data" / "processed" / "2025"
DOSSIER_SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "analyse_minus1"

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

FICHIERS = {
    "caracteristiques": DOSSIER / "caracteristiques_2025.csv",
    "lieux": DOSSIER / "lieux_2025.csv",
    "usagers": DOSSIER / "usagers_2025.csv",
    "vehicules": DOSSIER / "vehicules_2025.csv"
}

rapports = []

print("\n========== ANALYSE DES VALEURS -1 : BAAC 2025 ==========")

for nom, chemin in FICHIERS.items():

    print(f"\n========== TABLE : {nom.upper()} ==========")

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    total = len(df)

    print("Nombre de lignes :", total)

    for colonne in df.columns:

        nombre = (df[colonne].str.strip() == "-1").sum()

        if nombre > 0:

            pourcentage = round((nombre / total) * 100, 2)

            rapports.append({
                "table": nom,
                "colonne": colonne,
                "nombre_minus1": nombre,
                "pourcentage": pourcentage,
                "total_lignes": total
            })

            print(
                f"{colonne} : {nombre} valeurs "
                f"(-1) soit {pourcentage}%"
            )

rapport = pd.DataFrame(rapports)

if not rapport.empty:
    rapport = rapport.sort_values(
        by=["table", "nombre_minus1"],
        ascending=[True, False]
    )

    rapport.to_csv(
        DOSSIER_SORTIE / "rapport_detaille_minus1.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== RAPPORT GLOBAL ==========")
    print(rapport.to_string(index=False))

else:
    print("Aucune valeur -1 trouvée.")

print("\n========== TERMINÉ ==========")
print("Rapport enregistré dans :")
print(DOSSIER_SORTIE)
