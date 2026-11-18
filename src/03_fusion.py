
from pathlib import Path
import pandas as pd

# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOSSIER_ENTREE = BASE_DIR / "data" / "processed" / "2025" / "nettoye"
DOSSIER_SORTIE = BASE_DIR / "data" / "processed" / "2025" / "fusion"

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

FICHIERS = {
    "caracteristiques": "caracteristiques_2025.csv",
    "lieux": "lieux_2025.csv",
    "usagers": "usagers_2025.csv",
    "vehicules": "vehicules_2025.csv"
}

# =====================================================
# 2. IMPORTATION DES TABLES NETTOYEES
# =====================================================

print("\n========== FUSION BAAC 2025 ==========")
print("\n1. IMPORTATION DES DONNEES")

tables = {}

for nom, fichier in FICHIERS.items():

    chemin = DOSSIER_ENTREE / fichier

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    df = pd.read_csv(
        chemin,
        sep=";",
        dtype="string",
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    if "Num_Acc" not in df.columns:
        raise ValueError(
            f"La colonne Num_Acc est absente de {fichier}"
        )

    df["Num_Acc"] = df["Num_Acc"].str.strip()

    tables[nom] = df

    print(
        f"{nom.upper()} : "
        f"{len(df)} lignes, {len(df.columns)} colonnes"
    )

caracteristiques = tables["caracteristiques"]
lieux = tables["lieux"]
usagers = tables["usagers"]
vehicules = tables["vehicules"]

# =====================================================
# 3. VERIFICATION DES IDENTIFIANTS
# =====================================================

print("\n2. VERIFICATION DES IDENTIFIANTS")

if caracteristiques["Num_Acc"].isna().any():
    raise ValueError(
        "Des Num_Acc sont manquants dans Caracteristiques."
    )

doublons_accidents = caracteristiques[
    caracteristiques.duplicated(
        subset=["Num_Acc"],
        keep=False
    )
]

if not doublons_accidents.empty:
    raise ValueError(
        "La table Caracteristiques contient plusieurs "
        "lignes pour un même accident. Fusion interrompue."
    )

ids_accidents = set(caracteristiques["Num_Acc"].dropna())

rapport_relations = []

for nom, df in [
    ("lieux", lieux),
    ("usagers", usagers),
    ("vehicules", vehicules)
]:

    ids_enfants = set(df["Num_Acc"].dropna())

    ids_absents = ids_enfants - ids_accidents

    rapport_relations.append({
        "table": nom,
        "nombre_lignes": len(df),
        "nombre_accidents_distincts": len(ids_enfants),
        "identifiants_absents_caracteristiques": len(ids_absents)
    })

    print(
        f"{nom.upper()} : "
        f"{len(ids_absents)} identifiant(s) absent(s) "
        f"de Caracteristiques"
    )

rapport_relations = pd.DataFrame(rapport_relations)

# =====================================================
# 4. CREATION DES COMPTAGES PAR ACCIDENT
# =====================================================

print("\n3. CALCUL DES NOMBRES DE LIEUX, USAGERS ET VEHICULES")

def compter_par_accident(df, nom_colonne):

    resultat = (
        df.dropna(subset=["Num_Acc"])
          .groupby("Num_Acc")
          .size()
          .reset_index(name=nom_colonne)
    )

    return resultat


nb_lieux = compter_par_accident(
    lieux,
    "nombre_lieux"
)

nb_usagers = compter_par_accident(
    usagers,
    "nombre_usagers"
)

nb_vehicules = compter_par_accident(
    vehicules,
    "nombre_vehicules"
)

# =====================================================
# 5. CONSTRUCTION DE LA SYNTHESE PAR ACCIDENT
# =====================================================

print("\n4. CONSTRUCTION DE LA SYNTHESE")

synthese = caracteristiques.copy()

synthese = synthese.merge(
    nb_lieux,
    on="Num_Acc",
    how="left",
    validate="one_to_one"
)

synthese = synthese.merge(
    nb_usagers,
    on="Num_Acc",
    how="left",
    validate="one_to_one"
)

synthese = synthese.merge(
    nb_vehicules,
    on="Num_Acc",
    how="left",
    validate="one_to_one"
)

colonnes_comptage = [
    "nombre_lieux",
    "nombre_usagers",
    "nombre_vehicules"
]

synthese[colonnes_comptage] = (
    synthese[colonnes_comptage].fillna(0).astype("int64")
)

print(
    f"Nombre d'accidents dans la synthese : {len(synthese)}"
)

# =====================================================
# 6. ENREGISTREMENT DES TABLES
# =====================================================

print("\n5. ENREGISTREMENT DES RESULTATS")

resultats = {
    "accidents_2025.csv": caracteristiques,
    "lieux_2025.csv": lieux,
    "usagers_2025.csv": usagers,
    "vehicules_2025.csv": vehicules,
    "synthese_accidents_2025.csv": synthese
}

for fichier, df in resultats.items():

    chemin = DOSSIER_SORTIE / fichier

    df.to_csv(
        chemin,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"{fichier} : {len(df)} lignes")

# =====================================================
# 7. RAPPORT DES RELATIONS
# =====================================================

rapport_relations.to_csv(
    DOSSIER_SORTIE / "rapport_relations.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 8. VERIFICATION FINALE
# =====================================================

print("\n========== VERIFICATION FINALE ==========")

print(
    "Accidents dans Caracteristiques :",
    len(caracteristiques)
)

print(
    "Accidents dans la synthese :",
    len(synthese)
)

print(
    "Lignes Lieux conservees :",
    len(lieux)
)

print(
    "Lignes Usagers conservees :",
    len(usagers)
)

print(
    "Lignes Vehicules conservees :",
    len(vehicules)
)

print(
    "Doublons Num_Acc dans la synthese :",
    synthese["Num_Acc"].duplicated().sum()
)

print("\n========== FUSION TERMINEE ==========")

print("Resultats enregistres dans :")
print(DOSSIER_SORTIE)
