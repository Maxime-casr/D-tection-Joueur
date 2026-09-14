import matplotlib.pyplot as plt
import seaborn as sns


class Graphiques:
    def __init__(self, df):
        self.df = df

    def afficher_histogramme_ovr(self) -> plt.Figure:
        figure, axe = plt.subplots(figsize=(8, 5))
        sns.histplot(self.df, x="OVR", bins=15, color="green", ax=axe)
        axe.set_title("Distribution des notes générales")
        axe.set_xlabel("Note générale OVR")
        axe.set_ylabel("Nombre de joueurs")
        figure.tight_layout()
        return figure

    def afficher_comparaison_championnats(self) -> plt.Figure:
        championnats_principaux = self.df["League"].value_counts().head(6).index
        donnees = self.df[self.df["League"].isin(championnats_principaux)]
        moyennes = (
            donnees.groupby("League", as_index=False)["OVR"]
            .mean()
            .sort_values("OVR", ascending=False)
        )

        figure, axe = plt.subplots(figsize=(8, 5))
        sns.barplot(
            moyennes,
            x="League",
            y="OVR",
            hue="League",
            legend=False,
            ax=axe,
        )
        axe.set_title("OVR moyen par championnat")
        axe.set_xlabel("Championnat")
        axe.set_ylabel("OVR moyen")
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
            color="blue",
            alpha=0.7,
            ax=axe,
        )
        axe.set_title("Relation entre vitesse et dribble")
        axe.set_xlabel("Vitesse PAC")
        axe.set_ylabel("Dribble DRI")
        axe.set_xlim(20, 100)
        axe.set_ylim(20, 100)
        figure.tight_layout()
        return figure
