
import pandas as pd
from pathlib import Path

# ==================================================
# 1. CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw" / "2025"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "2025"
REPORT_DIR = OUTPUT_DIR / "rapports"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

fichiers = {
    "Caracteristiques": "caract-2025.csv",
    "Lieux": "lieux-2025.csv",
    "Usagers": "usagers-2025.csv",
    "Vehicules": "vehicules-2025.csv"
}

datasets = {}

resume = []
rapport_manquants = []
rapport_moins1 = []
rapport_integrite = []

print("\n========== PREPARATION BAAC 2025 ==========")


# ==================================================
# 2. IMPORTATION ET NORMALISATION
# ==================================================

print("\n========== 1. IMPORTATION ==========")

for nom, fichier in fichiers.items():

    chemin = DATA_DIR / fichier

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string"
    )

    # Nettoyer les noms des colonnes
    df.columns = df.columns.str.strip()

    # Nettoyer les espaces dans les valeurs
    for col in df.columns:
        df[col] = df[col].str.strip()

    # Transformer les chaînes vides en valeurs manquantes
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # Vérifier les colonnes dupliquées
    if df.columns.duplicated().any():
        raise ValueError(f"Colonnes dupliquées dans {nom}")

    datasets[nom] = df

    print(f"\n{nom}")
    print("Lignes :", len(df))
    print("Colonnes :", len(df.columns))


# ==================================================
# 3. SUPPRESSION DES DOUBLONS COMPLETS
# ==================================================

print("\n========== 2. DOUBLONS ==========")

for nom, df in datasets.items():

    avant = len(df)

    nombre_doublons = df.duplicated().sum()

    df = df.drop_duplicates().copy()

    datasets[nom] = df

    print(f"\n{nom}")
    print("Avant :", avant)
    print("Doublons supprimés :", nombre_doublons)
    print("Après :", len(df))

    resume.append({
        "Fichier": nom,
        "Lignes initiales": avant,
        "Doublons supprimés": nombre_doublons,
        "Lignes finales": len(df),
        "Colonnes": len(df.columns)
    })


# ==================================================
# 4. ANALYSE DES VALEURS MANQUANTES
# ==================================================

print("\n========== 3. VALEURS MANQUANTES ==========")

for nom, df in datasets.items():

    print(f"\n===== {nom} =====")

    for col in df.columns:

        nombre = df[col].isna().sum()

        pourcentage = round(
            nombre / len(df) * 100, 2
        ) if len(df) > 0 else 0

        if nombre > 0:

            print(
                f"{col} : {nombre} "
                f"({pourcentage} %)"
            )

        rapport_manquants.append({
            "Fichier": nom,
            "Colonne": col,
            "Nombre manquant": nombre,
            "Pourcentage (%)": pourcentage
        })


# ==================================================
# 5. AUDIT DES VALEURS -1
# ==================================================

print("\n========== 4. AUDIT DES VALEURS -1 ==========")

for nom, df in datasets.items():

    print(f"\n===== {nom} =====")

    for col in df.columns:

        serie = df[col].str.strip()

        masque = serie.isin(["-1", "-1.0"])

        nombre = masque.sum()

        if nombre > 0:

            pourcentage = round(
                nombre / len(df) * 100, 2
            )

            print(
                f"{col} : {nombre} "
                f"({pourcentage} %)"
            )

        rapport_moins1.append({
            "Fichier": nom,
            "Colonne": col,
            "Nombre de -1": nombre,
            "Pourcentage (%)": (
                round(nombre / len(df) * 100, 2)
                if len(df) > 0 else 0
            )
        })

# IMPORTANT :
# Les valeurs -1 sont conservées.
# Leur remplacement nécessite le dictionnaire BAAC
# et une décision adaptée à chaque variable.


# ==================================================
# 6. CONTROLE DES IDENTIFIANTS
# ==================================================

print("\n========== 5. IDENTIFIANTS ==========")

for nom, df in datasets.items():

    if "Num_Acc" not in df.columns:
        continue

    print(f"\n===== {nom} =====")

    print("Accidents distincts :", df["Num_Acc"].nunique())

    print(
        "Num_Acc manquants :",
        df["Num_Acc"].isna().sum()
    )

    print(
        "Lignes avec Num_Acc répété :",
        df["Num_Acc"].duplicated().sum()
    )


# ==================================================
# 7. CONTROLE DE L'INTEGRITE REFERENTIELLE
# ==================================================

print("\n========== 6. INTEGRITE REFERENTIELLE ==========")

caract = datasets["Caracteristiques"]

cles_valides = set(
    caract["Num_Acc"].dropna()
)

for nom in ["Lieux", "Usagers", "Vehicules"]:

    df = datasets[nom]

    cles = df["Num_Acc"]

    masque_orphelins = (
        cles.notna() &
        ~cles.isin(cles_valides)
    )

    nombre_orphelins = masque_orphelins.sum()

    nombre_sans_cle = cles.isna().sum()

    print(f"\n{nom}")

    print("Accidents absents de Caractéristiques :",
          nombre_orphelins)

    print("Identifiants manquants :", nombre_sans_cle)

    rapport_integrite.append({
        "Fichier": nom,
        "Identifiants orphelins": nombre_orphelins,
        "Identifiants manquants": nombre_sans_cle
    })


# ==================================================
# 8. EXPORTATION DES DONNEES PREPAREES
# ==================================================

print("\n========== 7. EXPORTATION ==========")

for nom, df in datasets.items():

    fichier_sortie = OUTPUT_DIR / f"{nom.lower()}_2025.csv"

    df.to_csv(
        fichier_sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig",
        na_rep=""
    )

    print("Fichier créé :", fichier_sortie)


# ==================================================
# 9. EXPORTATION DES RAPPORTS
# ==================================================

pd.DataFrame(resume).to_csv(
    REPORT_DIR / "resume_nettoyage.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_manquants).to_csv(
    REPORT_DIR / "valeurs_manquantes.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_moins1).to_csv(
    REPORT_DIR / "valeurs_minus1.csv",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_integrite).to_csv(
    REPORT_DIR / "integrite_referentielle.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==================================================
# 10. RESUME FINAL
# ==================================================

print("\n========== 8. RESUME FINAL ==========")

for nom, df in datasets.items():

    print(f"\n{nom}")

    print("Lignes :", len(df))
    print("Colonnes :", len(df.columns))

    print(
        "Valeurs manquantes :",
        df.isna().sum().sum()
    )

    print(
        "Doublons complets :",
        df.duplicated().sum()
    )

print("\n========== PREPARATION TERMINEE ==========")

print("\nDossier des données :", OUTPUT_DIR)
print("Dossier des rapports :", REPORT_DIR)
