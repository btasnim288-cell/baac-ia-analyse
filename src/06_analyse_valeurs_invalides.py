
import pandas as pd
from pathlib import Path

DOSSIER = Path("data/processed/2025")

colonnes_a_verifier = {
    "lieux_2025.csv": ["nbv", "pr", "pr1"],
    "usagers_2025.csv": ["actp"]
}

print("========== ANALYSE DES VALEURS NON NUMERIQUES ==========")

for fichier, colonnes in colonnes_a_verifier.items():

    df = pd.read_csv(
        DOSSIER / fichier,
        sep=";",
        dtype="string"
    )

    print(f"\n========== {fichier} ==========")

    for col in colonnes:

        valeurs = pd.to_numeric(df[col], errors="coerce")

        invalides = df.loc[
            df[col].notna() & valeurs.isna(),
            col
        ]

        print(f"\nColonne : {col}")
        print("Nombre de valeurs invalides :", len(invalides))
        print("Valeurs originales :")
        print(invalides.value_counts().head(20))

print("\n========== FIN DE L'ANALYSE ==========")
