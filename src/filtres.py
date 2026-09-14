class Filtres:
    def __init__(self, df):
        self.df = df

    def filtrer_par_championnat(self, championnat):
        if championnat != "Tous":
            self.df = self.df[self.df["League"] == championnat]
        return self.df

    def filtrer_par_poste(self, poste):
        if poste != "Tous":
            self.df = self.df[self.df["Position"] == poste]
        return self.df

    def filtrer_par_ovr(self, ovr_minimum):
        self.df = self.df[self.df["OVR"] >= ovr_minimum]
        return self.df
