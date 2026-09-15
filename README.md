# Tableau de bord de recrutement football

## Question métier
Quels joueurs et joueuses correspondent le mieux à un besoin de recrutement défini par le genre, l'âge, la nationalité, le championnat, le poste et le niveau général minimal ?
Le tableau de bord permet aux recruteurs de réduire rapidement le vivier puis de comparer les profils retenus.

## Choix des visualisations
L'histogramme montre la distribution de l'OVR, une variable numérique, et permet d'identifier les niveaux les plus fréquents.
Le diagramme en barres compare l'OVR moyen des six principaux championnats ou, après filtrage, des six principales équipes.
Son axe vertical commence à zéro afin de ne pas exagérer les écarts entre groupes.
Le nuage de points étudie la relation entre la vitesse (PAC) et le dribble (DRI), deux variables numériques.
La distribution des âges compare la composition des effectifs masculins et féminins.
La carte de chaleur synthétise les forces moyennes des huit postes les plus représentés.
Le radar facultatif compare exactement deux joueurs sur PAC, SHO, PAS, DRI et PHY avec un ordre d'axes fixe.
Chaque graphique comporte dans l'interface sa question, sa justification et une interprétation calculée sur la sélection.

## Utilisation
Installer les dépendances avec `pip install -e .` dans un environnement Python 3.12 ou plus récent.
Lancer l'application depuis la racine avec `streamlit run main.py`.
Les filtres de genre, championnat, poste, âge, OVR et nationalité mettent à jour les indicateurs, les graphiques, le radar et le tableau trié.

## Limite du dataset
Les notes proviennent d'EA Sports FC : elles représentent une évaluation de jeu vidéo et non des performances sportives observées en match.
Le dataset ne contient notamment ni coût de transfert, ni salaire, ni historique de blessures, indispensables à une décision réelle.
