import pandas as pd


class Filtres:
    def __init__(self, df):
        self.df = df

    def filtrer_par_championnat(self, championnat: str) -> pd.DataFrame:
        if championnat != "Tous":
            self.df = self.df[self.df["League"] == championnat]
        return self.df

    def filtrer_par_poste(self, poste: str) -> pd.DataFrame:
        if poste != "Tous":
            self.df = self.df[self.df["Position"] == poste]
        return self.df

    def filtrer_par_ovr(self, ovr_minimum: int) -> pd.DataFrame:
        self.df = self.df[self.df["OVR"] >= ovr_minimum]
        return self.df
