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

    def filtrer_par_genre(self, genres: list[str]) -> pd.DataFrame:
        if genres:
            self.df = self.df[self.df["gender"].isin(genres)]
        return self.df

    def filtrer_par_age(self, age_minimum: int, age_maximum: int) -> pd.DataFrame:
        self.df = self.df[self.df["Age"].between(age_minimum, age_maximum)]
        return self.df

    def filtrer_par_nation(self, nations: list[str]) -> pd.DataFrame:
        if nations:
            self.df = self.df[self.df["Nation"].isin(nations)]
        return self.df
