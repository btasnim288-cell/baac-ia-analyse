# Projet BAAC - L'IA pour l'analyse de données
Binôme : Tasnim / (nom du binôme)
Données : data.gouv.fr (BAAC 2025), téléchargées le 18/11/2026


## Structure du projet

- `data/` : fichiers BAAC 2025 (4 CSV, non versionnés)
- `src/` : scripts du pipeline, à exécuter dans l'ordre numérique
- `notebooks/` : analyses exploratoires
- `docs/` : documentation

## Pipeline de préparation (src/)

| Étape | Script | Rôle |
|---|---|---|
| 1 | 01_exploration | Découverte des 4 fichiers |
| 2 | 02_preparation | Import et typage |
| 3 | 03_fusion | Jointure des fichiers |
| 4 | 04_controle_qualite | Diagnostic qualité |
| 5-8 | 05 à 08 | Statistiques, valeurs invalides, anomalies, valeurs -1 |
| 9 | 09_classification_minus1 | Classement des valeurs -1 |
| 10-11 | 10, 11 | Vérification des doublons, lieux et véhicules |
| 12-13 | 12, 13 | Traitement et nettoyage final |
| 14 | 14_verification_finale | Contrôle du jeu de données final |