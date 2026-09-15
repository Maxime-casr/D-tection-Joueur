import pandas as pd


class Filtres:
    def __init__(self, df):
        self.df = df

    def filtrer_par_championnat(self, championnats: list[str]) -> pd.DataFrame:
        if championnats:
            self.df = self.df[self.df["League"].isin(championnats)]
        return self.df

    def filtrer_par_poste(self, postes: list[str]) -> pd.DataFrame:
        if postes:
            self.df = self.df[self.df["Position"].isin(postes)]
        return self.df

    def filtrer_par_ovr(self, ovr_minimum: int) -> pd.DataFrame:
        self.df = self.df[self.df["OVR"] >= ovr_minimum]
        return self.df
