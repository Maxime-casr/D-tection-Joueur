import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from constantes.constantes import POSTE
from src.filtres import Filtres
from src.graphiques import Graphiques


def lancer_app(df: pd.DataFrame):
    st.title("Tableau de bord de recrutement")
    st.caption(
        "Identifiez les meilleurs profils selon leur championnat, leur poste "
        "et leur niveau général."
    )

    championnats = sorted(df["League"].dropna().unique())
    postes = sorted(df["Position"].dropna().unique())

    with st.sidebar:
        st.header("Filtres")
        championnats_choisis = st.multiselect(
            "Championnats",
            options=championnats,
            placeholder="Tous les championnats",
        )
        postes_choisis = st.multiselect(
            "Postes",
            options=postes,
            format_func=lambda x: POSTE.get(x, x),
            placeholder="Tous les postes",
        )
        ovr_minimum = st.slider(
            "Note générale minimale (OVR)",
            min_value=int(df["OVR"].min()),
            max_value=int(df["OVR"].max()),
            value=75,
        )
        st.caption(f"{len(df):,} joueurs disponibles avant filtrage".replace(",", " "))

    filtres = Filtres(df)
    joueurs_filtres = filtres.filtrer_par_championnat(championnats_choisis)
    joueurs_filtres = filtres.filtrer_par_poste(postes_choisis)
    joueurs_filtres = filtres.filtrer_par_ovr(ovr_minimum)

    indicateur_nombre, indicateur_ovr, indicateur_pac, indicateur_dri = st.columns(4)
    indicateur_nombre.metric("Joueurs", len(joueurs_filtres))
    indicateur_ovr.metric(
        "OVR moyen",
        "—" if joueurs_filtres.empty else f"{joueurs_filtres['OVR'].mean():.1f}",
    )
    indicateur_pac.metric(
        "PAC moyen",
        "—" if joueurs_filtres.empty else f"{joueurs_filtres['PAC'].mean():.1f}",
    )
    indicateur_dri.metric(
        "DRI moyen",
        "—" if joueurs_filtres.empty else f"{joueurs_filtres['DRI'].mean():.1f}",
    )

    if joueurs_filtres.empty:
        st.warning("Aucun joueur ne correspond à ces critères. Élargissez les filtres.")
        return

    graphiques = Graphiques(joueurs_filtres)
    st.subheader("Analyse graphique")
    onglet_distribution, onglet_comparaison, onglet_relation = st.tabs(
        ["Distribution", "Comparaison", "Relation"]
    )

    with onglet_distribution:
        st.markdown(
            "**Question : comment se répartit le niveau des joueurs retenus ?**"
        )
        st.caption(
            "L’histogramme convient à une variable numérique continue et montre "
            "les zones de concentration des notes."
        )
        figure = graphiques.afficher_histogramme_ovr()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        st.info(
            f"Lecture : la moitié des joueurs se situe entre "
            f"{joueurs_filtres['OVR'].quantile(0.25):.0f} et "
            f"{joueurs_filtres['OVR'].quantile(0.75):.0f} d’OVR."
        )

    with onglet_comparaison:
        groupe = (
            "championnats" if joueurs_filtres["League"].nunique() > 1 else "équipes"
        )
        colonne_groupe = "League" if groupe == "championnats" else "Team"
        moyennes = joueurs_filtres.groupby(colonne_groupe)["OVR"].mean()
        meilleur_groupe = moyennes.idxmax()
        st.markdown(f"**Question : quels {groupe} affichent le meilleur OVR moyen ?**")
        st.caption(
            "Le diagramme en barres compare des catégories sur une même échelle; "
            "l’axe commence à zéro et six couleurs au maximum sont utilisées."
        )
        figure = graphiques.afficher_comparaison_championnats()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        st.info(
            f"Lecture : {meilleur_groupe} présente l’OVR moyen le plus élevé "
            f"({moyennes.max():.1f}) dans la sélection."
        )

    with onglet_relation:
        correlation = joueurs_filtres[["PAC", "DRI"]].corr().iloc[0, 1]
        intensite = (
            "forte"
            if abs(correlation) >= 0.7
            else "modérée"
            if abs(correlation) >= 0.4
            else "faible"
        )
        st.markdown(
            "**Question : les joueurs rapides sont-ils aussi de bons dribbleurs ?**"
        )
        st.caption(
            "Le nuage de points est adapté à deux variables numériques et révèle "
            "leur liaison ainsi que les profils atypiques."
        )
        figure = graphiques.afficher_relation_vitesse_dribble()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        if pd.isna(correlation):
            st.info(
                "Lecture : la sélection est trop homogène pour calculer une corrélation."
            )
        else:
            sens = "positive" if correlation >= 0 else "négative"
            st.info(
                f"Lecture : la relation est {intensite} et {sens} "
                f"(corrélation = {correlation:.2f})."
            )

    st.subheader("Face-à-face de joueurs")
    st.caption(
        "Le radar compare exactement deux profils sur cinq attributs; l’ordre des axes "
        "est fixe pour ne pas modifier artificiellement leur forme."
    )
    joueurs_tries = joueurs_filtres.sort_values("OVR", ascending=False)["Name"].tolist()
    if len(joueurs_tries) < 2:
        st.info(
            "Sélectionnez au moins deux joueurs avec les filtres pour afficher le radar."
        )
    else:
        colonne_joueur_1, colonne_joueur_2 = st.columns(2)
        joueur_1 = colonne_joueur_1.selectbox("Joueur 1", joueurs_tries, index=0)
        joueur_2 = colonne_joueur_2.selectbox("Joueur 2", joueurs_tries, index=1)
        if joueur_1 == joueur_2:
            st.warning(
                "Choisissez deux joueurs différents pour comparer leurs profils."
            )
        else:
            figure_radar = graphiques.afficher_radar_joueurs([joueur_1, joueur_2])
            st.pyplot(figure_radar, width="stretch")
            plt.close(figure_radar)

    st.subheader("Meilleurs profils")
    st.caption("Classement décroissant par OVR, puis par vitesse et dribble.")
    colonnes = ["Name", "Team", "League", "Position", "Age", "OVR", "PAC", "DRI"]
    meilleurs_profils = joueurs_filtres.sort_values(
        ["OVR", "PAC", "DRI"], ascending=False
    )[colonnes].head(20)
    meilleurs_profils = meilleurs_profils.rename(
        columns={
            "Name": "Joueur",
            "Team": "Équipe",
            "League": "Championnat",
            "Position": "Poste",
            "Age": "Âge",
        }
    )
    meilleurs_profils["Poste"] = meilleurs_profils["Poste"].map(
        lambda valeur: POSTE.get(valeur, valeur)
    )
    st.dataframe(
        meilleurs_profils,
        hide_index=True,
        width="stretch",
    )
