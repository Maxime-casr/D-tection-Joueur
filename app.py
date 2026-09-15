import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from constantes.constantes import POSTE
from src.filtres import Filtres
from src.graphiques import Graphiques
from src.valeur_marchante import afficher_valeur_marchande, memoriser_joueur_valeur

VARIABLES_ANALYSE = {
    "OVR": "Note générale (OVR)",
    "PAC": "Vitesse (PAC)",
    "SHO": "Tir (SHO)",
    "PAS": "Passe (PAS)",
    "DRI": "Dribble (DRI)",
    "DEF": "Défense (DEF)",
    "PHY": "Physique (PHY)",
    "Age": "Âge",
}


def lancer_app(df: pd.DataFrame):
    st.title("Tableau de bord de recrutement")
    st.caption("Explorez les profils des joueurs")

    championnats = sorted(df["League"].dropna().unique())
    postes = sorted(df["Position"].dropna().unique())
    nations = sorted(df["Nation"].dropna().unique())
    age_minimum_dataset = int(df["Age"].min())
    age_maximum_dataset = int(df["Age"].max())
    options_genre = {"Tous": [], "Hommes": ["M"], "Femmes": ["F"]}

    with st.sidebar:
        st.header("Filtres", icon=":material/filter_list:")
        genre_choisi = st.segmented_control(
            "Genre",
            options=options_genre,
            default="Tous",
            width="stretch",
        )
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
        ages_choisis = st.slider(
            "Tranche d’âge",
            min_value=age_minimum_dataset,
            max_value=age_maximum_dataset,
            value=(age_minimum_dataset, age_maximum_dataset),
        )
        ovr_minimum = st.slider(
            "Note générale minimale (OVR)",
            min_value=int(df["OVR"].min()),
            max_value=int(df["OVR"].max()),
            value=75,
        )
        nations_choisies = st.multiselect(
            "Nationalités",
            options=nations,
            placeholder="Toutes les nationalités",
        )
        st.caption(f"{len(df):,} joueurs disponibles avant filtrage".replace(",", " "))

    filtres = Filtres(df)
    joueurs_filtres = filtres.filtrer_par_genre(
        options_genre.get(genre_choisi or "Tous", [])
    )
    joueurs_filtres = filtres.filtrer_par_championnat(championnats_choisis)
    joueurs_filtres = filtres.filtrer_par_poste(postes_choisis)
    joueurs_filtres = filtres.filtrer_par_age(*ages_choisis)
    joueurs_filtres = filtres.filtrer_par_ovr(ovr_minimum)
    joueurs_filtres = filtres.filtrer_par_nation(nations_choisies)

    with st.container(horizontal=True):
        st.metric("Profils retenus", len(joueurs_filtres), border=True)
        st.metric(
            "OVR moyen",
            "—" if joueurs_filtres.empty else f"{joueurs_filtres['OVR'].mean():.1f}",
            border=True,
        )
        st.metric(
            "Âge moyen",
            "—"
            if joueurs_filtres.empty
            else f"{joueurs_filtres['Age'].mean():.1f} ans",
            border=True,
        )
        st.metric(
            "Meilleur OVR",
            "—" if joueurs_filtres.empty else int(joueurs_filtres["OVR"].max()),
            border=True,
        )

    if joueurs_filtres.empty:
        st.warning("Aucun joueur ne correspond à ces critères. Élargissez les filtres.")
        return

    graphiques = Graphiques(joueurs_filtres)
    st.subheader("Analyse graphique")
    (
        onglet_distribution,
        onglet_demographie,
        onglet_comparaison,
        onglet_postes,
        onglet_relation,
    ) = st.tabs(["Distribution", "Démographie", "Championnats", "Postes", "Relations"])

    with onglet_distribution:
        variable_distribution = st.selectbox(
            "Variable à analyser",
            options=list(VARIABLES_ANALYSE),
            format_func=lambda variable: VARIABLES_ANALYSE[variable],
            key="variable_distribution",
        )
        libelle_distribution = VARIABLES_ANALYSE[variable_distribution]
        st.markdown(f"**Comment se répartit {libelle_distribution.lower()} ?**")
        st.caption(
            "L’histogramme montre les zones de concentration, la ligne pointillée "
            "indique la médiane de la sélection."
        )
        figure = graphiques.afficher_distribution(
            variable_distribution, libelle_distribution
        )
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        st.info(
            f"Lecture : 50 % des profils se situent entre "
            f"{joueurs_filtres[variable_distribution].quantile(0.25):.0f} et "
            f"{joueurs_filtres[variable_distribution].quantile(0.75):.0f}."
        )

    with onglet_demographie:
        st.markdown("**Question : quels âges composent la sélection ?**")
        st.caption(
            "La distribution empilée permet de comparer les effectifs masculins "
            "et féminins à chaque âge."
        )
        figure = graphiques.afficher_distribution_age()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        st.info(
            f"Lecture : l’âge médian est de {joueurs_filtres['Age'].median():.0f} ans "
            f"et la sélection couvre {joueurs_filtres['Nation'].nunique()} nationalités."
        )

    with onglet_comparaison:
        groupe = (
            "championnats" if joueurs_filtres["League"].nunique() > 1 else "équipes"
        )
        colonne_groupe = "League" if groupe == "championnats" else "Team"
        moyennes = joueurs_filtres.groupby(colonne_groupe)["OVR"].mean()
        meilleur_groupe = moyennes.idxmax()
        st.markdown(f"**Question : quels {groupe} affichent le meilleur OVR moyen ?**")
        st.caption("Le diagramme en barres compare des catégories")
        figure = graphiques.afficher_comparaison_championnats()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        st.info(
            f"Lecture : {meilleur_groupe} présente l’OVR moyen le plus élevé "
            f"({moyennes.max():.1f}) dans la sélection."
        )

    with onglet_postes:
        st.markdown("**Question : quelles sont les forces moyennes de chaque poste ?**")
        st.caption(
            "La carte de chaleur compare six attributs sur les huit postes les plus "
            "représentés dans la sélection."
        )
        figure = graphiques.afficher_attributs_par_poste()
        st.pyplot(figure, width="stretch")
        plt.close(figure)
        poste_principal = joueurs_filtres["Position"].value_counts().idxmax()
        st.info(
            f"Lecture : {POSTE.get(poste_principal, poste_principal)} est le poste "
            f"le plus représenté ({(joueurs_filtres['Position'] == poste_principal).sum()} profils)."
        )

    with onglet_relation:
        colonne_x, colonne_y = st.columns(2)
        variable_x = colonne_x.selectbox(
            "Axe horizontal",
            options=list(VARIABLES_ANALYSE),
            index=1,
            format_func=lambda variable: VARIABLES_ANALYSE[variable],
            key="variable_relation_x",
        )
        variable_y = colonne_y.selectbox(
            "Axe vertical",
            options=list(VARIABLES_ANALYSE),
            index=4,
            format_func=lambda variable: VARIABLES_ANALYSE[variable],
            key="variable_relation_y",
        )
        mode_relation = st.segmented_control(
            "Affichage",
            options=["Densité", "Points par poste"],
            default="Densité",
            width="stretch",
            key="mode_relation",
        )
        if variable_x == variable_y:
            st.warning("Choisissez deux variables différentes pour les comparer.")
        else:
            libelle_x = VARIABLES_ANALYSE[variable_x]
            libelle_y = VARIABLES_ANALYSE[variable_y]
            correlation = joueurs_filtres[[variable_x, variable_y]].corr().iloc[0, 1]
            intensite = (
                "forte"
                if abs(correlation) >= 0.7
                else "modérée"
                if abs(correlation) >= 0.4
                else "faible"
            )
            st.markdown(
                f"**Quelle relation existe entre {libelle_x.lower()} et "
                f"{libelle_y.lower()} ?**"
            )
            if mode_relation == "Densité":
                st.caption(
                    "La couleur indique le nombre de profils dans chaque zone; la ligne "
                    "rouge montre la tendance générale."
                )
            else:
                st.caption(
                    "Les six postes principaux sont distingués et les autres "
                    "sont regroupés."
                )
            figure = graphiques.afficher_relation(
                variable_x,
                variable_y,
                libelle_x,
                libelle_y,
                mode_relation or "Densité",
            )
            st.pyplot(figure, width="stretch")
            plt.close(figure)
            if pd.isna(correlation):
                st.info(
                    "Lecture : la sélection est trop homogène pour calculer une corrélation."
                )
            else:
                st.info(f"Corrélation = {correlation:.2f}).")

    st.subheader("Face-à-face de joueurs", icon=":material/compare_arrows:")
    st.caption("Le radar compare deux profils sur cinq attributs")
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

    st.subheader("Meilleurs profils", icon=":material/leaderboard:")
    st.caption("Classement décroissant par OVR, puis par vitesse et dribble.")
    colonnes = [
        "Name",
        "gender",
        "Team",
        "League",
        "Nation",
        "Position",
        "Age",
        "OVR",
        "PAC",
        "DRI",
    ]
    meilleurs_profils = joueurs_filtres.sort_values(
        ["OVR", "PAC", "DRI"], ascending=False
    )[colonnes].head(20)
    meilleurs_profils = meilleurs_profils.rename(
        columns={
            "Name": "Joueur",
            "gender": "Genre",
            "Team": "Équipe",
            "League": "Championnat",
            "Nation": "Nationalité",
            "Position": "Poste",
            "Age": "Âge",
        }
    )
    meilleurs_profils["Genre"] = meilleurs_profils["Genre"].map(
        {"M": "Homme", "F": "Femme"}
    )
    meilleurs_profils["Poste"] = meilleurs_profils["Poste"].map(
        lambda valeur: POSTE.get(valeur, valeur)
    )
    meilleurs_profils = meilleurs_profils.reset_index(drop=True)
    meilleurs_profils["Valeur marchande"] = ":material/euro: Afficher"
    st.dataframe(
        meilleurs_profils,
        column_config={
            "Valeur marchande": st.column_config.ButtonColumn(
                "Valeur marchande",
                type="secondary",
                alignment="center",
                on_click=memoriser_joueur_valeur,
                args=(meilleurs_profils[["Joueur", "Équipe"]].copy(),),
                key="clic_valeur_marchande",
            )
        },
        hide_index=True,
        width="stretch",
    )

    joueur_selectionne = st.session_state.pop("joueur_valeur_selectionne", None)
    if joueur_selectionne:
        afficher_valeur_marchande(
            joueur_selectionne["nom"], joueur_selectionne["equipe"]
        )
