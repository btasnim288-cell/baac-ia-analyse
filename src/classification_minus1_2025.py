
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DOSSIER = BASE_DIR / "data" / "processed" / "2025"
SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "classification_minus1"

SORTIE.mkdir(parents=True, exist_ok=True)

FICHIERS = {
    "caracteristiques": DOSSIER / "caracteristiques_2025.csv",
    "lieux": DOSSIER / "lieux_2025.csv",
    "usagers": DOSSIER / "usagers_2025.csv",
    "vehicules": DOSSIER / "vehicules_2025.csv"
}

# Codes -1 explicitement documentés par l'ONISR
DOCUMENTES = {
    "caracteristiques": {
        "atm"
    },
    "lieux": {
        "circ", "vosp", "prof", "pr", "pr1",
        "plan", "surf", "infra", "situ"
    },
    "usagers": {
        "trajet", "secu1", "secu2", "secu3",
        "locp", "actp", "etatp"
    },
    "vehicules": {
        "senc", "obs", "obsm", "choc", "manv", "motor"
    }
}

rapports = []

print("\n========== CLASSIFICATION DES VALEURS -1 ==========")

for table, chemin in FICHIERS.items():

    df = pd.read_csv(
        chemin,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False
    )

    for colonne in df.columns:

        nombre = (df[colonne].str.strip() == "-1").sum()

        if nombre == 0:
            continue

        if colonne in DOCUMENTES[table]:
            statut = "DOCUMENTE : non renseigné"
            decision = "Conversion possible en valeur manquante"
        else:
            statut = "A VERIFIER dans la documentation"
            decision = "Conserver -1 provisoirement"

        rapports.append({
            "table": table,
            "colonne": colonne,
            "nombre_minus1": nombre,
            "pourcentage": round(nombre / len(df) * 100, 2),
            "statut_documentation": statut,
            "decision_proposee": decision
        })

rapport = pd.DataFrame(rapports)

rapport.to_csv(
    SORTIE / "classification_minus1_2025.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

print(rapport.to_string(index=False))

print("\n========== TERMINÉ ==========")
print("Rapport enregistré dans :", SORTIE)
