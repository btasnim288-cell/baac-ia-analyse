
import pandas as pd
from pathlib import Path

# ============================================================
# 1. CHEMINS DES FICHIERS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "raw" / "2025"

SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "analyse_anomalies"

SORTIE.mkdir(parents=True, exist_ok=True)

fichiers = {
    "Caracteristiques": DATA_DIR / "caract-2025.csv",
    "Usagers": DATA_DIR / "usagers-2025.csv",
    "Vehicules": DATA_DIR / "vehicules-2025.csv"
}


# ============================================================
# 2. IMPORTATION DES DONNEES
# ============================================================

print("\n========== IMPORTATION ==========")

datasets = {}

for nom, chemin in fichiers.items():

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    df.columns = df.columns.str.strip()

    for colonne in df.columns:
        df[colonne] = df[colonne].str.strip()

    df = df.replace(r"^\s*$", pd.NA, regex=True)

    datasets[nom] = df

    print(f"{nom} : {len(df)} lignes")


caract = datasets["Caracteristiques"]
usagers = datasets["Usagers"]
vehicules = datasets["Vehicules"]


# ============================================================
# 3. IDENTIFICATION DES QUATRE VEHICULES
# ============================================================

print("\n========== VEHICULES A ANALYSER ==========")

anomalies = pd.DataFrame({
    "Num_Acc": [
        "202500013215",
        "202500013431",
        "202500034910",
        "202500042211"
    ],
    "id_vehicule": [
        "155 952 166",
        "155 951 755",
        "155 914 063",
        "155 901 257"
    ]
})

print(anomalies)


# ============================================================
# 4. VERIFICATION DANS CARACTERISTIQUES
# ============================================================

print("\n========== VERIFICATION DES ACCIDENTS ==========")

details_accidents = caract.merge(
    anomalies[["Num_Acc"]],
    on="Num_Acc",
    how="inner"
)

print(details_accidents.to_string(index=False))

details_accidents.to_csv(
    SORTIE / "details_accidents.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 5. VERIFICATION DANS VEHICULES
# ============================================================

print("\n========== VERIFICATION DES VEHICULES ==========")

details_vehicules = vehicules.merge(
    anomalies,
    on=["Num_Acc", "id_vehicule"],
    how="inner"
)

print(details_vehicules.to_string(index=False))

details_vehicules.to_csv(
    SORTIE / "details_vehicules.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. RECHERCHE DES USAGERS DES MEMES ACCIDENTS
# ============================================================

print("\n========== USAGERS DES MEMES ACCIDENTS ==========")

usagers_memes_accidents = usagers.merge(
    anomalies[["Num_Acc"]],
    on="Num_Acc",
    how="inner"
)

print(usagers_memes_accidents.to_string(index=False))

usagers_memes_accidents.to_csv(
    SORTIE / "usagers_memes_accidents.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. RECHERCHE DES IDENTIFIANTS DANS TOUTE LA TABLE USAGERS
# ============================================================

print("\n========== RECHERCHE DES ID_VEHICULE ==========")

recherche_ids = usagers.merge(
    anomalies[["id_vehicule"]],
    on="id_vehicule",
    how="inner"
)

print(recherche_ids.to_string(index=False))

recherche_ids.to_csv(
    SORTIE / "recherche_identifiants_usagers.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. COMPARAISON AVEC NUM_VEH
# ============================================================

print("\n========== COMPARAISON NUM_VEH ==========")

comparaison_num_veh = anomalies.merge(
    vehicules[["Num_Acc", "id_vehicule", "num_veh"]],
    on=["Num_Acc", "id_vehicule"],
    how="left"
)

comparaison_num_veh = comparaison_num_veh.merge(
    usagers[["Num_Acc", "id_vehicule", "num_veh"]],
    on=["Num_Acc", "id_vehicule"],
    how="left",
    suffixes=("_vehicule", "_usager")
)

print(comparaison_num_veh.to_string(index=False))

comparaison_num_veh.to_csv(
    SORTIE / "comparaison_num_veh.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. RAPPORT DE SYNTHESE
# ============================================================

print("\n========== RAPPORT DE SYNTHESE ==========")

rapport = []

for _, anomalie in anomalies.iterrows():

    num_acc = anomalie["Num_Acc"]
    id_vehicule = anomalie["id_vehicule"]

    accident_existe = (
        caract["Num_Acc"] == num_acc
    ).any()

    vehicule_existe = (
        (vehicules["Num_Acc"] == num_acc)
        & (vehicules["id_vehicule"] == id_vehicule)
    ).any()

    usager_meme_accident = (
        usagers["Num_Acc"] == num_acc
    ).sum()

    usager_meme_identifiant = (
        (usagers["Num_Acc"] == num_acc)
        & (usagers["id_vehicule"] == id_vehicule)
    ).sum()

    identifiant_autre_accident = (
        (usagers["id_vehicule"] == id_vehicule)
        & (usagers["Num_Acc"] != num_acc)
    ).sum()

    rapport.append({
        "Num_Acc": num_acc,
        "id_vehicule": id_vehicule,
        "accident_existe": accident_existe,
        "vehicule_existe": vehicule_existe,
        "nombre_usagers_meme_accident": int(usager_meme_accident),
        "nombre_usagers_meme_identifiant": int(usager_meme_identifiant),
        "identifiant_trouve_autre_accident": int(identifiant_autre_accident)
    })


rapport = pd.DataFrame(rapport)

print(rapport.to_string(index=False))

rapport.to_csv(
    SORTIE / "rapport_synthese_anomalies.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. FIN
# ============================================================

print("\n========== ANALYSE TERMINEE ==========")

print("Tous les rapports sont enregistrés dans :")
print(SORTIE)
