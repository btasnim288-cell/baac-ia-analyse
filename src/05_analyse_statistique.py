
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 1. CONFIGURATION
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOSSIER_ENTREE = BASE_DIR / "data" / "processed" / "2025" / "fusion"
DOSSIER_SORTIE = BASE_DIR / "data" / "exploration" / "2025" / "analyse_statistique"
DOSSIER_GRAPHIQUES = DOSSIER_SORTIE / "graphiques"

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
DOSSIER_GRAPHIQUES.mkdir(parents=True, exist_ok=True)

print("\n========== ANALYSE STATISTIQUE BAAC 2025 ==========")

# Stockage des graphiques pour les afficher ensemble
graphiques = []

# =====================================================
# 2. IMPORTATION DES DONNEES
# =====================================================

def charger_table(nom):
    chemin = DOSSIER_ENTREE / nom

    if not chemin.exists():
        raise FileNotFoundError(f"Fichier introuvable : {chemin}")

    return pd.read_csv(
        chemin,
        sep=";",
        dtype="string",
        encoding="utf-8-sig"
    )

accidents = charger_table("accidents_2025.csv")
usagers = charger_table("usagers_2025.csv")
vehicules = charger_table("vehicules_2025.csv")

print("\n1. IMPORTATION")
print("Accidents :", len(accidents))
print("Usagers :", len(usagers))
print("Vehicules :", len(vehicules))

# =====================================================
# 3. PREPARATION DES DATES ET HEURES
# =====================================================

print("\n2. PREPARATION DES VARIABLES")

if "date_accident" in accidents.columns:
    accidents["date_analyse"] = pd.to_datetime(
        accidents["date_accident"],
        errors="coerce",
        dayfirst=True
    )
else:
    accidents["date_analyse"] = pd.to_datetime(
        dict(
            year=pd.to_numeric(accidents["an"], errors="coerce"),
            month=pd.to_numeric(accidents["mois"], errors="coerce"),
            day=pd.to_numeric(accidents["jour"], errors="coerce")
        ),
        errors="coerce"
    )

accidents["mois_analyse"] = accidents["date_analyse"].dt.month

jours_fr = {
    0: "Lundi",
    1: "Mardi",
    2: "Mercredi",
    3: "Jeudi",
    4: "Vendredi",
    5: "Samedi",
    6: "Dimanche"
}

accidents["jour_semaine"] = (
    accidents["date_analyse"].dt.dayofweek.map(jours_fr)
)

if "hrmn" in accidents.columns:
    heure_brute = accidents["hrmn"].str.strip()

    heures = heure_brute.str.extract(
        r"^(\d{1,2})\s*:?\s*\d{2}$",
        expand=False
    )

    accidents["heure_analyse"] = pd.to_numeric(
        heures,
        errors="coerce"
    )

elif "heure_accident" in accidents.columns:
    heures = accidents["heure_accident"].str.extract(
        r"^(\d{1,2})",
        expand=False
    )

    accidents["heure_analyse"] = pd.to_numeric(
        heures,
        errors="coerce"
    )
else:
    accidents["heure_analyse"] = pd.NA

# =====================================================
# 4. FONCTION POUR AJOUTER UN GRAPHIQUE
# =====================================================

def ajouter_graphique(fig, nom):
    fig.savefig(
        DOSSIER_GRAPHIQUES / f"{nom}.png",
        dpi=300,
        bbox_inches="tight"
    )
    graphiques.append(fig)

# =====================================================
# 5. FONCTION FREQUENCES
# =====================================================

def enregistrer_frequences(df, colonne, nom, titre):

    if colonne not in df.columns:
        print(f"Variable absente : {colonne}")
        return

    serie = df[colonne].fillna("Non renseigné").astype(str)

    frequences = (
        serie.value_counts()
        .rename_axis("categorie")
        .reset_index(name="nombre")
    )

    frequences.to_csv(
        DOSSIER_SORTIE / f"{nom}.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n{titre}")
    print(frequences.to_string(index=False))

    donnees = frequences.head(15).copy()

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        donnees["categorie"].astype(str),
        donnees["nombre"]
    )

    ax.set_title(titre, fontsize=12, fontweight="bold")
    ax.set_xlabel("Catégorie")
    ax.set_ylabel("Nombre")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    ajouter_graphique(fig, nom)

# =====================================================
# 6. FONCTION COMPTAGE
# =====================================================

def enregistrer_comptage(serie, nom, titre, ordre=None):

    frequences = serie.value_counts().sort_index()

    if ordre is not None:
        frequences = frequences.reindex(ordre, fill_value=0)

    frequences.index.name = "categorie"
    resultat = frequences.rename("nombre").reset_index()

    resultat.to_csv(
        DOSSIER_SORTIE / f"{nom}.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n{titre}")
    print(resultat.to_string(index=False))

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        resultat["categorie"].astype(str),
        resultat["nombre"]
    )

    ax.set_title(titre, fontsize=12, fontweight="bold")
    ax.set_xlabel("Catégorie")
    ax.set_ylabel("Nombre d'accidents")
    ax.tick_params(axis="x", rotation=45)

    fig.tight_layout()
    ajouter_graphique(fig, nom)

# =====================================================
# 7. ANALYSE TEMPORELLE
# =====================================================

print("\n3. ANALYSE TEMPORELLE")

enregistrer_comptage(
    accidents["mois_analyse"].dropna().astype(int),
    "accidents_par_mois",
    "Accidents par mois",
    ordre=list(range(1, 13))
)

ordre_jours = [
    "Lundi", "Mardi", "Mercredi",
    "Jeudi", "Vendredi", "Samedi", "Dimanche"
]

enregistrer_comptage(
    accidents["jour_semaine"].dropna(),
    "accidents_par_jour",
    "Accidents par jour de la semaine",
    ordre=ordre_jours
)

enregistrer_comptage(
    accidents["heure_analyse"].dropna().astype(int),
    "accidents_par_heure",
    "Accidents par heure",
    ordre=list(range(24))
)

# =====================================================
# 8. CONDITIONS D'ACCIDENT
# =====================================================

print("\n4. ANALYSE DES CONDITIONS")

enregistrer_frequences(
    accidents, "lum",
    "accidents_par_luminosite",
    "Accidents selon la luminosité"
)

enregistrer_frequences(
    accidents, "atm",
    "accidents_par_atmosphere",
    "Accidents selon les conditions atmosphériques"
)

enregistrer_frequences(
    accidents, "col",
    "accidents_par_collision",
    "Accidents selon le type de collision"
)

# =====================================================
# 9. ANALYSE DES USAGERS
# =====================================================

print("\n5. ANALYSE DES USAGERS")

enregistrer_frequences(
    usagers, "grav",
    "gravite_usagers",
    "Répartition des usagers selon la gravité"
)

enregistrer_frequences(
    usagers, "sexe",
    "usagers_par_sexe",
    "Répartition des usagers selon le sexe"
)

enregistrer_frequences(
    usagers, "catu",
    "usagers_par_categorie",
    "Répartition des usagers par catégorie"
)

# =====================================================
# 10. ANALYSE DES VEHICULES
# =====================================================

print("\n6. ANALYSE DES VEHICULES")

enregistrer_frequences(
    vehicules, "catv",
    "vehicules_par_categorie",
    "Répartition des véhicules par catégorie"
)

# =====================================================
# 11. ANALYSE GEOGRAPHIQUE
# =====================================================

print("\n7. ANALYSE GEOGRAPHIQUE")

enregistrer_frequences(
    accidents, "dep",
    "accidents_par_departement",
    "Répartition des accidents par département"
)

# =====================================================
# 12. STATISTIQUES GENERALES
# =====================================================

print("\n8. STATISTIQUES GENERALES")

statistiques = pd.DataFrame([
    {"indicateur": "Nombre d'accidents", "valeur": len(accidents)},
    {"indicateur": "Nombre d'usagers", "valeur": len(usagers)},
    {"indicateur": "Nombre de véhicules", "valeur": len(vehicules)},
    {
        "indicateur": "Accidents sans date exploitable",
        "valeur": accidents["date_analyse"].isna().sum()
    },
    {
        "indicateur": "Accidents sans heure exploitable",
        "valeur": accidents["heure_analyse"].isna().sum()
    }
])

print(statistiques.to_string(index=False))

statistiques.to_csv(
    DOSSIER_SORTIE / "statistiques_generales.csv",
    sep=";",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 13. AFFICHAGE DE TOUS LES GRAPHIQUES
# =====================================================

print("\n9. AFFICHAGE DE TOUS LES GRAPHIQUES")

nombre = len(graphiques)
colonnes = 2
lignes = (nombre + colonnes - 1) // colonnes

fig_tableau, axes = plt.subplots(
    lignes,
    colonnes,
    figsize=(18, 5 * lignes)
)

axes = axes.flatten()

for i, graphique in enumerate(graphiques):

    ancien_ax = graphique.axes[0]

    # Copier le graphique dans le tableau de bord
    for barre in ancien_ax.patches:
        axes[i].bar(
            [barre.get_x() + barre.get_width() / 2],
            [barre.get_height()],
            width=barre.get_width(),
            align="center"
        )

    axes[i].set_title(
        ancien_ax.get_title(),
        fontsize=11,
        fontweight="bold"
    )

    axes[i].set_xlabel(ancien_ax.get_xlabel())
    axes[i].set_ylabel(ancien_ax.get_ylabel())

    etiquettes = [
        t.get_text() for t in ancien_ax.get_xticklabels()
    ]

    axes[i].set_xticks(range(len(etiquettes)))
    axes[i].set_xticklabels(etiquettes, rotation=45, ha="right")

    plt.close(graphique)

# Supprimer les cases vides
for j in range(nombre, len(axes)):
    fig_tableau.delaxes(axes[j])

fig_tableau.suptitle(
    "TABLEAU DE BORD STATISTIQUE - ACCIDENTS BAAC 2025",
    fontsize=18,
    fontweight="bold"
)

fig_tableau.tight_layout(rect=[0, 0, 1, 0.98])

plt.show()

print("\n========== ANALYSE TERMINEE ==========")
print("Graphiques PNG :", DOSSIER_GRAPHIQUES)
