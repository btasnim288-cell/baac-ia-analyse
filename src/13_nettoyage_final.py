
import pandas as pd
from pathlib import Path

# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent

# Les fichiers préparés se trouvent directement ici
DOSSIER_ENTREE = BASE_DIR / "data" / "processed" / "2025"

# Les fichiers nettoyés seront enregistrés ici
DOSSIER_SORTIE = BASE_DIR / "data" / "processed" / "2025" / "nettoye"

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

FICHIERS = {
    "caracteristiques": "caracteristiques_2025.csv",
    "lieux": "lieux_2025.csv",
    "usagers": "usagers_2025.csv",
    "vehicules": "vehicules_2025.csv"
}

# =====================================================
# 2. COLONNES A TRAITER
# =====================================================

# Colonnes retenues provisoirement comme documentées
# avec -1 = information non renseignée.
#
# Les autres colonnes contenant -1 sont conservées
# jusqu'à vérification dans le dictionnaire BAAC.

COLONNES_MINUS1 = {
    "caracteristiques": [
        "atm"
    ],

    "lieux": [
        "circ",
        "vosp",
        "prof",
        "pr",
        "pr1",
        "plan",
        "surf",
        "infra",
        "situ"
    ],

    "usagers": [
        "trajet",
        "secu1",
        "secu2",
        "secu3",
        "locp",
        "actp",
        "etatp"
    ],

    "vehicules": [
        "senc",
        "obs",
        "obsm",
        "choc",
        "manv",
        "motor"
    ]
}

# =====================================================
# 3. INITIALISATION DES RAPPORTS
# =====================================================

rapports = []
bilan_tables = []

print("\n========== NETTOYAGE FINAL BAAC 2025 ==========")

# =====================================================
# 4. TRAITEMENT DES QUATRE TABLES
# =====================================================

for table, nom_fichier in FICHIERS.items():

    chemin = DOSSIER_ENTREE / nom_fichier

    print("\n------------------------------------------")
    print("TABLE :", table.upper())
    print("------------------------------------------")

    # Vérification de l'existence du fichier
    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    # Importation
    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    lignes_avant = len(df)
    colonnes_avant = len(df.columns)

    print("Lignes avant :", lignes_avant)
    print("Colonnes :", colonnes_avant)

    total_converti = 0

    # Colonnes contenant des -1 à traiter
    for colonne in COLONNES_MINUS1[table]:

        if colonne not in df.columns:
            print("ATTENTION : colonne absente :", colonne)
            continue

        # Nombre de -1 avant traitement
        masque = df[colonne].str.strip().eq("-1").fillna(False)

        nombre = int(masque.sum())

        # Conversion de -1 en valeur manquante
        df.loc[masque, colonne] = pd.NA

        total_converti += nombre

        rapports.append({
            "table": table,
            "colonne": colonne,
            "valeurs_converties": nombre,
            "decision": "Converties en valeur manquante"
        })

        print(
            f"{colonne} : {nombre} valeurs -1 converties"
        )

    # Vérification des lignes
    lignes_apres = len(df)

    assert lignes_avant == lignes_apres, (
        f"Erreur : le nombre de lignes a changé dans {table}"
    )

    # Nombre de valeurs manquantes après nettoyage
    total_manquants = int(df.isna().sum().sum())

    # Sauvegarde
    sortie = DOSSIER_SORTIE / nom_fichier

    df.to_csv(
        sortie,
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nLignes après :", lignes_apres)
    print("Valeurs converties :", total_converti)
    print("Valeurs manquantes totales :", total_manquants)
    print("Fichier enregistré :", sortie)

    bilan_tables.append({
        "table": table,
        "lignes_avant": lignes_avant,
        "lignes_apres": lignes_apres,
        "colonnes": colonnes_avant,
        "valeurs_converties": total_converti,
        "valeurs_manquantes_apres": total_manquants
    })

# =====================================================
# 5. GENERATION DES RAPPORTS
# =====================================================

rapport = pd.DataFrame(rapports)

rapport.to_csv(
    DOSSIER_SORTIE / "rapport_nettoyage_final.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

bilan = pd.DataFrame(bilan_tables)

bilan.to_csv(
    DOSSIER_SORTIE / "bilan_nettoyage_final.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 6. VERIFICATION DES VALEURS -1 RESTANTES
# =====================================================

print("\n========== VERIFICATION DES -1 RESTANTS ==========")

for table, nom_fichier in FICHIERS.items():

    chemin = DOSSIER_SORTIE / nom_fichier

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    print(f"\nTABLE : {table.upper()}")

    trouve = False

    for colonne in df.columns:

        nombre = int(
            df[colonne].str.strip().eq("-1").sum()
        )

        if nombre > 0:
            trouve = True
            print(f"{colonne} : {nombre} valeurs -1 conservées")

    if not trouve:
        print("Aucune valeur -1 restante.")

# =====================================================
# 7. BILAN FINAL
# =====================================================

print("\n========== BILAN FINAL ==========")
print(bilan.to_string(index=False))

print("\n========== RAPPORT DES CONVERSIONS ==========")
print(rapport.to_string(index=False))

print("\nAucune ligne n'a été supprimée.")
print("Les fichiers sources sont conservés.")
print("Les colonnes non vérifiées ont été conservées.")
print("\nNETTOYAGE TERMINE AVEC SUCCES.")

print("\nDossier de sortie :")
print(DOSSIER_SORTIE)
