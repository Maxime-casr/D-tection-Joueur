# Tableau de bord de recrutement

## Question métier
L’outil aide la cellule de recrutement à trouver des profils selon le championnat, le poste et des seuils OVR, PAC et DRI.
Le scénario initial cible un ailier rapide et bon dribbleur, hors des cinq grands championnats, avec une note supérieure à 75.

## Lancement
Installer les dépendances avec `uv sync` (ou `pip install -e .`).
Exécuter ensuite `uv run streamlit run main.py` (ou `streamlit run main.py`).

## Choix visuels
L’histogramme montre la distribution des notes OVR et permet de repérer le niveau typique du vivier.
Le barplot compare l’OVR moyen des six championnats les plus représentés sur une échelle commune partant de zéro.
Le nuage de points mesure la relation entre vitesse et dribble, deux critères clés pour un ailier.
Limite : les notes issues d’un jeu ne couvrent ni les contrats ni les performances réelles observées sur le terrain.
