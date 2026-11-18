
import pandas as pd
from pathlib import Path

print("========== CONVERSION DES TYPES - BAAC 2025 ==========")

DOSSIER = Path("data/processed/2025")
SORTIE = DOSSIER / "types"
SORTIE.mkdir(parents=True, exist_ok=True)

# Colonnes à conserver comme identifiants ou texte
colonnes_texte = {
    "caracteristiques_2025": [
        "Num_Acc", "dep", "com", "adr", "hrmn"
    ],
    "lieux_2025": [
        "Num_Acc", "voie", "v2", "nbv"
    ],
    "usagers_2025": [
        "Num_Acc", "id_usager", "id_vehicule", "num_veh", "actp"
    ],
    "vehicules_2025": [
        "Num_Acc", "id_vehicule", "num_veh"
    ]
}

# Colonnes pouvant contenir des décimales
colonnes_decimales = {
    "caracteristiques_2025": ["lat", "long"],
    "lieux_2025": ["lartpc", "larrout"]
}

fichiers = {
    "caracteristiques_2025": "caracteristiques_2025.csv",
    "lieux_2025": "lieux_2025.csv",
    "usagers_2025": "usagers_2025.csv",
    "vehicules_2025": "vehicules_2025.csv"
}

rapports = []

for nom, fichier in fichiers.items():

    print(f"\n========== {nom.upper()} ==========")

    df = pd.read_csv(
        DOSSIER / fichier,
        sep=";",
        dtype="string"
    )

    texte = colonnes_texte[nom]
    decimales = colonnes_decimales.get(nom, [])

    for col in df.columns:

        if col in texte:
            continue

        # Nettoyage des espaces dans PR et PR1
        if nom == "lieux_2025" and col in ["pr", "pr1"]:
            df[col] = (
                df[col]
                .str.replace(" ", "", regex=False)
                .str.replace("\u00a0", "", regex=False)
            )

        # Conversion numérique
        valeurs = pd.to_numeric(
            df[col].str.replace(",", ".", regex=False),
            errors="coerce"
        )

        # Nombre de valeurs non vides impossibles à convertir
        invalides = (
            df[col].notna() & valeurs.isna()
        ).sum()

        if col in decimales:
            df[col] = valeurs.astype("Float64")
            type_final = "Décimal"

        else:
            # Vérifier si les valeurs sont entières
            non_entieres = (
                valeurs.notna() & (valeurs % 1 != 0)
            ).sum()

            if non_entieres == 0:
                df[col] = valeurs.astype("Int64")
                type_final = "Entier"
            else:
                df[col] = valeurs.astype("Float64")
                type_final = "Décimal"

        rapports.append({
            "table": nom,
            "colonne": col,
            "type_final": type_final,
            "valeurs_invalides": int(invalides),
            "valeurs_manquantes": int(df[col].isna().sum())
        })

    # Création de la date et de l'heure
    if nom == "caracteristiques_2025":

        df["date_accident"] = pd.to_datetime(
            {
                "year": df["an"],
                "month": df["mois"],
                "day": df["jour"]
            },
            errors="coerce"
        )

        heure = pd.to_datetime(
            df["hrmn"],
            format="%H:%M",
            errors="coerce"
        )

        df["heure_accident"] = (
            heure.dt.strftime("%H:%M").astype("string")
        )

    # Exportation
    fichier_sortie = SORTIE / f"{nom}_types.csv"

    df.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("Nombre de lignes :", len(df))
    print("Fichier exporté :", fichier_sortie)

# Rapport global
rapport = pd.DataFrame(rapports)

rapport.to_csv(
    SORTIE / "rapport_conversion_global.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print("\n========== RAPPORT GLOBAL ==========")
print(rapport.to_string(index=False))

print("\nConversion terminée !")
print("Dossier des résultats :", SORTIE)
