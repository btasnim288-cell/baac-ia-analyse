
import pandas as pd
from pathlib import Path

print("========== CONTROLE QUALITE BAAC 2025 ==========")

DOSSIER = Path("data/processed/2025")
DOSSIER_TYPES = DOSSIER / "types"
SORTIE = DOSSIER / "qualite"
SORTIE.mkdir(parents=True, exist_ok=True)

# Charger les quatre tables converties
fichiers = {
    "caracteristiques": "caracteristiques_2025_types.csv",
    "lieux": "lieux_2025_types.csv",
    "usagers": "usagers_2025_types.csv",
    "vehicules": "vehicules_2025_types.csv"
}

tables = {}

for nom, fichier in fichiers.items():
    tables[nom] = pd.read_csv(
        DOSSIER_TYPES / fichier,
        sep=";",
        dtype_backend="numpy_nullable"
    )

car = tables["caracteristiques"]
usa = tables["usagers"]

controles = []

def ajouter_controle(table, controle, nombre, observation):
    controles.append({
        "table": table,
        "controle": controle,
        "nombre": int(nombre),
        "observation": observation
    })

# 1. Contrôle des dates
dates_invalides = car["date_accident"].isna().sum()

ajouter_controle(
    "caracteristiques",
    "Dates invalides",
    dates_invalides,
    "Date impossible ou manquante"
)

# 2. Contrôle des heures
heures_invalides = car["heure_accident"].isna().sum()

ajouter_controle(
    "caracteristiques",
    "Heures invalides",
    heures_invalides,
    "Heure impossible ou manquante"
)

# 3. Contrôle des coordonnées
lat_invalides = (
    (car["lat"] < -90) | (car["lat"] > 90)
).fillna(False).sum()

long_invalides = (
    (car["long"] < -180) | (car["long"] > 180)
).fillna(False).sum()

ajouter_controle(
    "caracteristiques",
    "Latitudes hors limites",
    lat_invalides,
    "Latitude hors intervalle -90 à 90"
)

ajouter_controle(
    "caracteristiques",
    "Longitudes hors limites",
    long_invalides,
    "Longitude hors intervalle -180 à 180"
)

# 4. Contrôle de l'année de naissance
annees_invalides = (
    (usa["an_nais"] < 1900) | (usa["an_nais"] > 2025)
).fillna(False).sum()

ajouter_controle(
    "usagers",
    "Années de naissance hors limites",
    annees_invalides,
    "Année antérieure à 1900 ou postérieure à 2025"
)

# 5. Calcul de l'âge lorsque l'année de naissance existe
usa["age_2025"] = 2025 - usa["an_nais"]

ages_invalides = (
    (usa["age_2025"] < 0) | (usa["age_2025"] > 110)
).fillna(False).sum()

ajouter_controle(
    "usagers",
    "Âges hors limites",
    ages_invalides,
    "Âge négatif ou supérieur à 110 ans"
)

# 6. Vérifier les valeurs -1
for nom, df in tables.items():
    for colonne in df.columns:
        if pd.api.types.is_numeric_dtype(df[colonne]):
            nombre = (df[colonne] == -1).sum()

            if nombre > 0:
                ajouter_controle(
                    nom,
                    f"Valeurs -1 dans {colonne}",
                    nombre,
                    "Code à interpréter avec le dictionnaire BAAC"
                )

# 7. Exporter le rapport
rapport = pd.DataFrame(controles)

rapport.to_csv(
    SORTIE / "rapport_controle_qualite.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# 8. Affichage
print("\n========== RESULTATS ==========")
print(rapport.to_string(index=False))

print("\nRapport enregistré dans :", SORTIE)
print("\n========== FIN DU CONTROLE ==========")
