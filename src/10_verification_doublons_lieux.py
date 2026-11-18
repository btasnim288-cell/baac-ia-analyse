
import pandas as pd
from pathlib import Path

# ==========================================
# 1. CHEMINS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

FICHIER = BASE_DIR / "data" / "raw" / "2025" / "lieux-2025.csv"

DOSSIER_SORTIE = (
    BASE_DIR / "data" / "exploration" / "2025"
    / "verification_doublons"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. IMPORTATION
# ==========================================

print("\n========== IMPORTATION ==========")

df = pd.read_csv(
    FICHIER,
    sep=";",
    encoding="utf-8-sig",
    dtype="string",
    low_memory=False
)

df.columns = df.columns.str.strip()

for col in df.columns:
    df[col] = df[col].str.strip()

df = df.replace(r"^\s*$", pd.NA, regex=True)

print("Nombre de lignes :", len(df))
print("Nombre de colonnes :", len(df.columns))


# ==========================================
# 3. DETECTION DES DOUBLONS COMPLETS
# ==========================================

print("\n========== DOUBLONS COMPLETS ==========")

doublons = df[df.duplicated(keep=False)].copy()

print("Nombre de lignes concernées :", len(doublons))
print("Nombre de lignes supplémentaires :", df.duplicated().sum())

if not doublons.empty:

    doublons = doublons.sort_values(
        by="Num_Acc",
        na_position="last"
    )

    print(doublons.to_string(index=False))

    doublons.to_csv(
        DOSSIER_SORTIE / "details_doublons_lieux.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


# ==========================================
# 4. ANALYSE PAR ACCIDENT
# ==========================================

print("\n========== DOUBLONS PAR ACCIDENT ==========")

if not doublons.empty:

    resume = (
        doublons.groupby("Num_Acc", dropna=False)
        .size()
        .reset_index(name="nombre_lignes")
    )

    print(resume.to_string(index=False))

    resume.to_csv(
        DOSSIER_SORTIE / "resume_doublons_par_accident.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )


# ==========================================
# 5. VERIFICATION DES REPETITIONS NUM_ACC
# ==========================================

print("\n========== REPETITIONS NUM_ACC ==========")

repetitions = (
    df.groupby("Num_Acc", dropna=False)
    .size()
    .reset_index(name="nombre_lignes")
)

print("Nombre de Num_Acc distincts :", df["Num_Acc"].nunique())
print("Nombre de Num_Acc manquants :", df["Num_Acc"].isna().sum())

repetitions.to_csv(
    DOSSIER_SORTIE / "repetitions_num_acc.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 6. DETECTION DES DOUBLONS SUR NUM_ACC SEUL
# ==========================================

print("\n========== REPETITIONS NUM_ACC SEUL ==========")

doublons_acc = df[
    df.duplicated(subset=["Num_Acc"], keep=False)
].copy()

print("Lignes concernées :", len(doublons_acc))
print("Nombre de Num_Acc répétés :",
      doublons_acc["Num_Acc"].nunique())

doublons_acc.to_csv(
    DOSSIER_SORTIE / "details_repetitions_num_acc.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 7. CONCLUSION
# ==========================================

print("\n========== CONCLUSION ==========")

print("Aucune ligne n'a été supprimée.")
print("Les résultats doivent être interprétés avant correction.")

print("\nAnalyse terminée.")
print("Rapports enregistrés dans :")
print(DOSSIER_SORTIE)
