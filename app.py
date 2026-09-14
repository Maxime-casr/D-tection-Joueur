import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.filtres import Filtres
from src.graphiques import Graphiques


def lancer_app(df: pd.DataFrame):
    st.title("Tableau de bord de recrutement")
    st.caption("Filtrez les joueurs par championnat, poste et note générale.")

    championnats = sorted(df["League"].dropna().unique())
    postes = sorted(df["Position"].dropna().unique())

    with st.sidebar:
        st.header("Filtres")
        championnat = st.selectbox("Championnat", options=["Tous"] + championnats)
        poste = st.selectbox("Poste", options=["Tous"] + postes)
        ovr_minimum = st.slider(
            "OVR minimum",
            min_value=int(df["OVR"].min()),
            max_value=int(df["OVR"].max()),
            value=75,
        )

    filtres = Filtres(df)
    joueurs_filtres = filtres.filtrer_par_championnat(championnat)
    joueurs_filtres = filtres.filtrer_par_poste(poste)
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
        st.warning("Aucun joueur ne correspond à ces critères.")
        return

    graphiques = Graphiques(joueurs_filtres)
    st.subheader("Analyse graphique")
    graphique_choisi = st.selectbox(
        "Graphique à afficher",
        [
            "Distribution des notes",
            "Comparaison des championnats",
            "Relation vitesse-dribble",
        ],
    )

    if graphique_choisi == "Distribution des notes":
        figure = graphiques.afficher_histogramme_ovr()
        justification = (
            "L’histogramme montre comment les notes générales se répartissent "
            "dans la sélection."
        )
    elif graphique_choisi == "Comparaison des championnats":
        figure = graphiques.afficher_comparaison_championnats()
        justification = (
            "Le barplot compare l’OVR moyen des six championnats les plus "
            "représentés, avec un axe partant de zéro."
        )
    else:
        figure = graphiques.afficher_relation_vitesse_dribble()
        justification = (
            "Le nuage de points permet de repérer les joueurs à la fois rapides "
            "et bons dribbleurs."
        )

    st.pyplot(figure, width="stretch")
    st.caption(justification)
    plt.close(figure)

    st.subheader("Meilleurs profils")
    colonnes = ["Name", "Team", "League", "Position", "OVR", "PAC", "DRI"]
    st.dataframe(
        joueurs_filtres.sort_values(
            ["OVR", "PAC", "DRI"], ascending=False
        )[colonnes].head(20),
        hide_index=True,
        width="stretch",
    )
