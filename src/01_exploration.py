
import pandas as pd
from pathlib import Path

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data" / "raw" / "2025"

SORTIE = BASE_DIR / "data" / "exploration" / "2025"
SORTIE.mkdir(parents=True, exist_ok=True)

fichiers = {
    "Caracteristiques": DATA_DIR / "caract-2025.csv",
    "Lieux": DATA_DIR / "lieux-2025.csv",
    "Usagers": DATA_DIR / "usagers-2025.csv",
    "Vehicules": DATA_DIR / "vehicules-2025.csv"
}


# ============================================================
# 2. IMPORTATION ET NETTOYAGE INITIAL
# ============================================================

print("\n========== IMPORTATION DES DONNEES ==========")

datasets = {}

for nom, chemin in fichiers.items():

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    # Nettoyage des noms des colonnes
    df.columns = df.columns.str.strip()

    # Vérification des colonnes dupliquées
    if df.columns.duplicated().any():
        colonnes = df.columns[
            df.columns.duplicated()
        ].tolist()

        raise ValueError(
            f"Colonnes dupliquées dans {nom} : {colonnes}"
        )

    # Nettoyage des espaces
    for colonne in df.columns:
        df[colonne] = df[colonne].str.strip()

    # Transformation des chaînes vides en valeurs manquantes
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    datasets[nom] = df

    print(f"\n{nom}")
    print("Nombre de lignes :", len(df))
    print("Nombre de colonnes :", len(df.columns))
    print("Colonnes :", list(df.columns))


# Récupération des quatre tables

caract = datasets["Caracteristiques"]
lieux = datasets["Lieux"]
usagers = datasets["Usagers"]
vehicules = datasets["Vehicules"]


# ============================================================
# 3. EXPLORATION GENERALE
# ============================================================

print("\n========== EXPLORATION GENERALE ==========")

resume_general = []

for nom, df in datasets.items():

    print(f"\n========== {nom.upper()} ==========")

    print("\nDimensions :")
    print(df.shape)

    print("\nTypes des colonnes :")
    print(df.dtypes)

    print("\nPremières lignes :")
    print(df.head())

    print("\nInformations générales :")
    df.info()

    resume_general.append({
        "table": nom,
        "nombre_lignes": len(df),
        "nombre_colonnes": len(df.columns),
        "nombre_doublons": int(df.duplicated().sum()),
        "nombre_valeurs_manquantes": int(
            df.isna().sum().sum()
        )
    })


pd.DataFrame(resume_general).to_csv(
    SORTIE / "resume_general.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 4. ANALYSE DES VALEURS MANQUANTES ET DES DOUBLONS
# ============================================================

print("\n========== QUALITE DES DONNEES ==========")

rapport_manquants = []
rapport_doublons = []

for nom, df in datasets.items():

    print(f"\n========== {nom.upper()} ==========")

    # Analyse des valeurs manquantes

    manquants = df.isna().sum()

    pourcentage = (
        manquants / len(df) * 100
    ).round(2)

    bilan = pd.DataFrame({
        "table": nom,
        "colonne": df.columns,
        "nombre_manquants": manquants.values,
        "pourcentage_manquants": pourcentage.values
    })

    print("\nValeurs manquantes :")

    print(
        bilan[bilan["nombre_manquants"] > 0].to_string(
            index=False
        )
    )

    rapport_manquants.extend(
        bilan.to_dict("records")
    )

    # Analyse des doublons complets

    nombre_doublons = int(df.duplicated().sum())

    print("\nNombre de doublons complets :")
    print(nombre_doublons)

    rapport_doublons.append({
        "table": nom,
        "nombre_doublons_complets": nombre_doublons
    })

    # Nombre de valeurs distinctes

    print("\nNombre de valeurs distinctes :")
    print(df.nunique(dropna=True))


pd.DataFrame(rapport_manquants).to_csv(
    SORTIE / "rapport_valeurs_manquantes.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

pd.DataFrame(rapport_doublons).to_csv(
    SORTIE / "rapport_doublons.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 5. ANALYSE DE L'IDENTIFIANT NUM_ACC
# ============================================================

print("\n========== ANALYSE DE NUM_ACC ==========")

rapport_cles = []

for nom, df in datasets.items():

    if "Num_Acc" not in df.columns:
        print(f"Attention : Num_Acc absente dans {nom}")
        continue

    nombre_total = len(df)

    nombre_manquant = int(
        df["Num_Acc"].isna().sum()
    )

    nombre_distinct = int(
        df["Num_Acc"].nunique()
    )

    nombre_repetitions = (
        int(df["Num_Acc"].notna().sum())
        - nombre_distinct
    )

    print(f"\n========== {nom.upper()} ==========")

    print("Nombre de lignes :", nombre_total)
    print("Num_Acc distincts :", nombre_distinct)
    print("Num_Acc manquants :", nombre_manquant)
    print("Occurrences répétées :", nombre_repetitions)

    rapport_cles.append({
        "table": nom,
        "nombre_lignes": nombre_total,
        "nombre_Num_Acc_distincts": nombre_distinct,
        "nombre_Num_Acc_manquants": nombre_manquant,
        "nombre_occurrences_repetees": nombre_repetitions
    })


pd.DataFrame(rapport_cles).to_csv(
    SORTIE / "rapport_cles_Num_Acc.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. ANALYSE DES DOUBLONS DANS LA TABLE LIEUX
# ============================================================

print("\n========== DOUBLONS DU FICHIER LIEUX ==========")

doublons_lieux = lieux[
    lieux.duplicated(keep=False)
].copy()

nombre_doublons_lieux = int(
    lieux.duplicated().sum()
)

print(
    "Nombre de lignes dupliquées au-delà de la première occurrence :",
    nombre_doublons_lieux
)

print(
    "Nombre total de lignes concernées :",
    len(doublons_lieux)
)

print("\nDétails des doublons :")
print(doublons_lieux)

doublons_lieux.to_csv(
    SORTIE / "doublons_lieux.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. VERIFICATION DES RELATIONS USAGERS / VEHICULES
# ============================================================

print("\n========== RELATIONS USAGERS / VEHICULES ==========")

colonnes_cles = [
    "Num_Acc",
    "id_vehicule"
]

# Vérification des colonnes nécessaires

for nom, df in [
    ("Usagers", usagers),
    ("Vehicules", vehicules)
]:

    for colonne in colonnes_cles:

        if colonne not in df.columns:
            raise ValueError(
                f"Colonne {colonne} absente dans {nom}"
            )


# Récupération des clés distinctes non manquantes

cles_usagers = (
    usagers[colonnes_cles]
    .dropna()
    .drop_duplicates()
)

cles_vehicules = (
    vehicules[colonnes_cles]
    .dropna()
    .drop_duplicates()
)


# Jointure externe pour comparer les deux tables

comparaison = cles_usagers.merge(
    cles_vehicules,
    on=colonnes_cles,
    how="outer",
    indicator=True
)


# Calcul des relations

relations_communes = int(
    (comparaison["_merge"] == "both").sum()
)

relations_usagers_sans_vehicule = int(
    (comparaison["_merge"] == "left_only").sum()
)

relations_vehicules_sans_usager = int(
    (comparaison["_merge"] == "right_only").sum()
)


print(
    "\nRelations présentes dans les deux fichiers :",
    relations_communes
)

print(
    "Relations Usagers sans véhicule correspondant :",
    relations_usagers_sans_vehicule
)

print(
    "Relations Véhicules sans usager correspondant :",
    relations_vehicules_sans_usager
)


# Extraction des usagers sans véhicule correspondant

usagers_sans_vehicule = comparaison[
    comparaison["_merge"] == "left_only"
][colonnes_cles]

details_usagers = usagers.merge(
    usagers_sans_vehicule,
    on=colonnes_cles,
    how="inner"
)

print("\nDétails des usagers sans véhicule :")
print(details_usagers)


# Extraction des véhicules sans usager correspondant

vehicules_sans_usager = comparaison[
    comparaison["_merge"] == "right_only"
][colonnes_cles]

details_vehicules = vehicules.merge(
    vehicules_sans_usager,
    on=colonnes_cles,
    how="inner"
)

print("\nDétails des véhicules sans usager :")
print(details_vehicules)


# Exportation des résultats

details_usagers.to_csv(
    SORTIE / "details_usagers_sans_vehicule.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

details_vehicules.to_csv(
    SORTIE / "details_vehicules_sans_usager.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

comparaison[
    comparaison["_merge"] != "both"
].to_csv(
    SORTIE / "relations_sans_correspondance.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# Rapport global des relations

pd.DataFrame([{
    "relations_communes": relations_communes,
    "usagers_sans_vehicule": relations_usagers_sans_vehicule,
    "vehicules_sans_usager": relations_vehicules_sans_usager
}]).to_csv(
    SORTIE / "rapport_relations.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. RECHERCHE DES VALEURS -1
# ============================================================

print("\n========== RECHERCHE DES VALEURS -1 ==========")

rapport_moins_un = []

for nom, df in datasets.items():

    print(f"\n========== {nom.upper()} ==========")

    trouve = False

    for colonne in df.columns:

        valeurs = df[colonne].str.strip()

        nombre = int(
            valeurs.isin(["-1", "-1.0"]).sum()
        )

        if nombre > 0:

            print(f"{colonne} : {nombre}")

            rapport_moins_un.append({
                "table": nom,
                "colonne": colonne,
                "nombre_valeurs_moins_un": nombre
            })

            trouve = True

    if not trouve:
        print("Aucune valeur -1 détectée.")


pd.DataFrame(
    rapport_moins_un,
    columns=[
        "table",
        "colonne",
        "nombre_valeurs_moins_un"
    ]
).to_csv(
    SORTIE / "rapport_valeurs_moins_un.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. INTEGRITE REFERENTIELLE AVEC CARACTERISTIQUES
# ============================================================

print(
    "\n========== INTEGRITE REFERENTIELLE NUM_ACC =========="
)

# Identifiants des accidents dans Caractéristiques

cles_accidents = set(
    caract["Num_Acc"].dropna()
)

rapport_integrite = []

for nom, df in [
    ("Lieux", lieux),
    ("Usagers", usagers),
    ("Vehicules", vehicules)
]:

    cles_secondaires = set(
        df["Num_Acc"].dropna()
    )

    # Identifiants secondaires absents de Caractéristiques

    absents = cles_secondaires - cles_accidents

    # Identifiants manquants

    manquants = int(
        df["Num_Acc"].isna().sum()
    )

    print(f"\n{nom}")

    print(
        "Num_Acc absents de Caractéristiques :",
        len(absents)
    )

    print(
        "Num_Acc manquants :",
        manquants
    )

    rapport_integrite.append({
        "table": nom,
        "accidents_non_trouves": len(absents),
        "Num_Acc_manquants": manquants
    })


pd.DataFrame(rapport_integrite).to_csv(
    SORTIE / "rapport_integrite_referentielle.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. RESUME FINAL
# ============================================================

print("\n========== RESUME FINAL ==========")

resume_final = []

for nom, df in datasets.items():

    nombre_lignes = len(df)

    nombre_colonnes = len(df.columns)

    nombre_manquants = int(
        df.isna().sum().sum()
    )

    nombre_doublons = int(
        df.duplicated().sum()
    )

    print(f"\n{nom}")

    print("Lignes :", nombre_lignes)
    print("Colonnes :", nombre_colonnes)
    print("Valeurs manquantes :", nombre_manquants)
    print("Doublons complets :", nombre_doublons)

    resume_final.append({
        "table": nom,
        "nombre_lignes": nombre_lignes,
        "nombre_colonnes": nombre_colonnes,
        "nombre_valeurs_manquantes": nombre_manquants,
        "nombre_doublons": nombre_doublons
    })


pd.DataFrame(resume_final).to_csv(
    SORTIE / "resume_final.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. FIN DU TRAITEMENT
# ============================================================

print("\n========== FICHIERS GENERES ==========")

for fichier in sorted(SORTIE.glob("*.csv")):
    print("-", fichier.name)

print("\nDossier des rapports :")
print(SORTIE)

print("\n========== EXPLORATION TERMINEE ==========")
