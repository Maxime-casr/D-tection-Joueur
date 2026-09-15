import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class Graphiques:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid", context="notebook")

    def afficher_histogramme_ovr(self) -> plt.Figure:
        figure, axe = plt.subplots(figsize=(8, 5))
        sns.histplot(
            self.df,
            x="OVR",
            bins=15,
            color="#168AAD",
            edgecolor="white",
            ax=axe,
        )
        axe.set_title("Distribution des notes générales")
        axe.set_xlabel("Note générale OVR (sur 99)")
        axe.set_ylabel("Nombre de joueurs")
        axe.set_xlim(0, 99)
        figure.tight_layout()
        return figure

    def afficher_comparaison_championnats(self) -> plt.Figure:
        colonne_groupe = "League" if self.df["League"].nunique() > 1 else "Team"
        groupes_principaux = self.df[colonne_groupe].value_counts().head(6).index
        donnees = self.df[self.df[colonne_groupe].isin(groupes_principaux)]
        moyennes = (
            donnees.groupby(colonne_groupe, as_index=False)["OVR"]
            .mean()
            .sort_values("OVR", ascending=False)
        )

        figure, axe = plt.subplots(figsize=(8, 5))
        sns.barplot(
            moyennes,
            x=colonne_groupe,
            y="OVR",
            hue=colonne_groupe,
            palette="colorblind",
            legend=False,
            ax=axe,
        )
        libelle_groupe = "championnat" if colonne_groupe == "League" else "équipe"
        axe.set_title(f"OVR moyen par {libelle_groupe}")
        axe.set_xlabel(libelle_groupe.capitalize())
        axe.set_ylabel("OVR moyen (sur 99)")
        axe.set_ylim(0, 99)
        axe.tick_params(axis="x", rotation=25)
        figure.tight_layout()
        return figure

    def afficher_relation_vitesse_dribble(self) -> plt.Figure:
        figure, axe = plt.subplots(figsize=(8, 5))
        sns.scatterplot(
            self.df,
            x="PAC",
            y="DRI",
            color="#E76F51",
            alpha=0.75,
            ax=axe,
        )
        axe.set_title("Relation entre vitesse et dribble")
        axe.set_xlabel("Vitesse PAC (sur 99)")
        axe.set_ylabel("Dribble DRI (sur 99)")
        axe.set_xlim(0, 99)
        axe.set_ylim(0, 99)
        figure.tight_layout()
        return figure

    def afficher_radar_joueurs(self, noms_joueurs: list[str]) -> plt.Figure:
        statistiques = ["PAC", "SHO", "PAS", "DRI", "PHY"]
        angles = np.linspace(0, 2 * np.pi, len(statistiques), endpoint=False).tolist()
        angles += angles[:1]

        figure, axe = plt.subplots(figsize=(7, 7), subplot_kw={"polar": True})
        couleurs = sns.color_palette("colorblind", n_colors=len(noms_joueurs))

        for nom, couleur in zip(noms_joueurs, couleurs):
            joueur = self.df.loc[self.df["Name"] == nom].iloc[0]
            valeurs = joueur[statistiques].astype(float).tolist()
            valeurs += valeurs[:1]
            axe.plot(angles, valeurs, linewidth=2, label=nom, color=couleur)
            axe.fill(angles, valeurs, alpha=0.12, color=couleur)

        axe.set_xticks(angles[:-1], statistiques)
        axe.set_ylim(0, 99)
        axe.set_yticks([20, 40, 60, 80], ["20", "40", "60", "80"])
        axe.set_title("Comparaison des profils techniques", pad=24)
        axe.legend(loc="upper right", bbox_to_anchor=(1.25, 1.12))
        figure.tight_layout()
        return figure
