import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from constantes.constantes import POSTE
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
        poste = st.selectbox(
            "Poste", options=["Tous"] + postes, format_func=lambda x: POSTE.get(x, x)
        )
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
        " " if joueurs_filtres.empty else f"{joueurs_filtres['OVR'].mean():.2f}",
    )
    indicateur_pac.metric(
        "PAC moyen",
        " " if joueurs_filtres.empty else f"{joueurs_filtres['PAC'].mean():.2f}",
    )
    indicateur_dri.metric(
        "DRI moyen",
        " " if joueurs_filtres.empty else f"{joueurs_filtres['DRI'].mean():.2f}",
    )

    if joueurs_filtres.empty:
        st.warning("Aucun joueur.")
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

    elif graphique_choisi == "Comparaison des championnats":
        figure = graphiques.afficher_comparaison_championnats()

    else:
        figure = graphiques.afficher_relation_vitesse_dribble()

    st.pyplot(figure, width="stretch")
    plt.close(figure)

    st.subheader("Meilleurs profils")
    colonnes = ["Name", "Team", "League", "Position", "OVR", "PAC", "DRI"]
    st.dataframe(
        joueurs_filtres.sort_values(["OVR", "PAC", "DRI"], ascending=False)[
            colonnes
        ].head(20),
        hide_index=True,
        width="stretch",
    )
