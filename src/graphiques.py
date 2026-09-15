import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from constantes.constantes import POSTE


class Graphiques:
    def __init__(self, df):
        self.df = df
        sns.set_theme(style="whitegrid", context="notebook")

    def afficher_distribution(self, variable: str, libelle: str) -> plt.Figure:
        figure, axe = plt.subplots(figsize=(8, 5))
        sns.histplot(
            self.df,
            x=variable,
            bins=15,
            color="#168AAD",
            edgecolor="white",
            ax=axe,
        )
        axe.axvline(
            self.df[variable].median(),
            color="#E76F51",
            linestyle="--",
            linewidth=2,
            label="Médiane",
        )
        axe.set_title(f"Distribution de {libelle.lower()}")
        axe.set_xlabel(libelle)
        axe.set_ylabel("Nombre de joueurs")
        axe.legend()
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

    def afficher_relation(
        self,
        variable_x: str,
        variable_y: str,
        libelle_x: str,
        libelle_y: str,
        mode: str = "Densité",
    ) -> plt.Figure:
        donnees = self.df[[variable_x, variable_y, "Position"]].dropna()
        figure, axe = plt.subplots(figsize=(9, 5.5))

        if mode == "Densité":
            densite = axe.hexbin(
                donnees[variable_x],
                donnees[variable_y],
                gridsize=32,
                mincnt=1,
                cmap=sns.light_palette("#075E54", as_cmap=True),
                linewidths=0.2,
            )
            figure.colorbar(densite, ax=axe, label="Nombre de profils")
            axe.grid(alpha=0.2)
        else:
            postes_principaux = donnees["Position"].value_counts().head(12).index
            donnees_points = donnees.sample(
                n=min(len(donnees), 1_500), random_state=42
            ).copy()
            donnees_points["Poste affiché"] = (
                donnees_points["Position"]
                .where(donnees_points["Position"].isin(postes_principaux), "Autres")
                .map(lambda poste: POSTE.get(poste, poste))
            )
            sns.scatterplot(
                donnees_points,
                x=variable_x,
                y=variable_y,
                hue="Poste affiché",
                alpha=0.5,
                s=24,
                linewidth=0,
                ax=axe,
            )
            axe.legend(title="Poste", bbox_to_anchor=(1.02, 1), loc="upper left")

        if donnees[variable_x].nunique() > 1 and donnees[variable_y].nunique() > 1:
            sns.regplot(
                donnees,
                x=variable_x,
                y=variable_y,
                scatter=False,
                ci=None,
                color="#D1495B",
                line_kws={"linewidth": 2, "label": "Tendance"},
                ax=axe,
            )

        axe.set_title(f"Relation entre {libelle_x.lower()} et {libelle_y.lower()}")
        axe.set_xlabel(libelle_x)
        axe.set_ylabel(libelle_y)
        figure.tight_layout()
        return figure

    def afficher_distribution_age(self) -> plt.Figure:
        donnees = self.df.assign(
            Genre=self.df["gender"].map({"M": "Hommes", "F": "Femmes"})
        )
        figure, axe = plt.subplots(figsize=(8, 5))
        sns.histplot(
            donnees,
            x="Age",
            hue="Genre",
            multiple="stack",
            bins=range(int(donnees["Age"].min()), int(donnees["Age"].max()) + 2),
            palette={"Hommes": "#168AAD", "Femmes": "#E76F51"},
            edgecolor="white",
            ax=axe,
        )
        axe.set_title("Répartition des joueurs par âge")
        axe.set_xlabel("Âge")
        axe.set_ylabel("Nombre de joueurs")
        figure.tight_layout()
        return figure

    def afficher_attributs_par_poste(self) -> plt.Figure:
        statistiques = ["PAC", "SHO", "PAS", "DRI", "DEF", "PHY"]
        postes_principaux = self.df["Position"].value_counts().head(8).index
        moyennes = (
            self.df[self.df["Position"].isin(postes_principaux)]
            .groupby("Position")[statistiques]
            .mean()
        )
        moyennes.index = [POSTE.get(poste, poste) for poste in moyennes.index]

        figure, axe = plt.subplots(figsize=(9, 5))
        sns.heatmap(
            moyennes,
            annot=True,
            fmt=".0f",
            cmap="YlGnBu",
            vmin=30,
            vmax=90,
            linewidths=0.5,
            cbar_kws={"label": "Note moyenne"},
            ax=axe,
        )
        axe.set_title("Forces moyennes des principaux postes")
        axe.set_xlabel("Attribut")
        axe.set_ylabel("")
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
