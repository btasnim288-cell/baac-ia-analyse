
import pandas as pd
from pathlib import Path

# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

DOSSIER = BASE_DIR / "data" / "processed" / "2025" / "nettoye"

SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "verification_finale"

SORTIE.mkdir(parents=True, exist_ok=True)

FICHIERS = {
    "caracteristiques": "caracteristiques_2025.csv",
    "lieux": "lieux_2025.csv",
    "usagers": "usagers_2025.csv",
    "vehicules": "vehicules_2025.csv"
}

resultats = []
rapport_manquants = []
rapport_doublons = []

# ==========================================
# 2. VERIFICATION DES TABLES
# ==========================================

print("\n========== VERIFICATION FINALE BAAC 2025 ==========")

for table, fichier in FICHIERS.items():

    chemin = DOSSIER / fichier

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier absent : {chemin}")

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    print(f"\n========== {table.upper()} ==========")

    lignes = len(df)
    colonnes = len(df.columns)

    print("Nombre de lignes :", lignes)
    print("Nombre de colonnes :", colonnes)

    # Nombre de valeurs manquantes
    total_na = int(df.isna().sum().sum())

    # Valeurs -1 restantes
    total_moins1 = 0

    for colonne in df.columns:

        nombre_na = int(df[colonne].isna().sum())

        nombre_moins1 = int(
            df[colonne].str.strip().eq("-1").sum()
        )

        total_moins1 += nombre_moins1

        if nombre_na > 0:
            rapport_manquants.append({
                "table": table,
                "colonne": colonne,
                "valeurs_manquantes": nombre_na,
                "pourcentage": round(nombre_na / lignes * 100, 2)
            })

    # Doublons complets
    doublons = int(df.duplicated().sum())

    rapport_doublons.append({
        "table": table,
        "doublons_complets": doublons
    })

    # Identifiant accident
    id_manquants = int(df["Num_Acc"].isna().sum())

    print("Valeurs manquantes :", total_na)
    print("Valeurs -1 restantes :", total_moins1)
    print("Doublons complets :", doublons)
    print("Num_Acc manquants :", id_manquants)

    resultats.append({
        "table": table,
        "lignes": lignes,
        "colonnes": colonnes,
        "valeurs_manquantes": total_na,
        "valeurs_moins1_restantes": total_moins1,
        "doublons_complets": doublons,
        "Num_Acc_manquants": id_manquants
    })

# ==========================================
# 3. ENREGISTREMENT DES RAPPORTS
# ==========================================

pd.DataFrame(resultats).to_csv(
    SORTIE / "bilan_verification_finale.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_manquants).to_csv(
    SORTIE / "detail_valeurs_manquantes.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_doublons).to_csv(
    SORTIE / "controle_doublons_final.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 4. AFFICHAGE DU BILAN
# ==========================================

print("\n========== BILAN GENERAL ==========")

print(pd.DataFrame(resultats).to_string(index=False))

print("\n========== CONTROLE TERMINE ==========")
print("Rapports enregistrés dans :", SORTIE)
