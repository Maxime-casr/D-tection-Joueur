from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "all_players_clean.csv"
BIG_FIVE = {
    "Premier League",
    "LALIGA EA SPORTS",
    "Serie A Enilive",
    "Bundesliga",
    "Ligue 1 McDonald's",
}
POSTE = {
    "CM": "Milieu central",
    "GK": "Gardien",
    "CB": "Défenseur central",
    "RB": "Arrière droit",
    "LB": "Arrière gauche",
    "CDM": "Milieu défensif",
    "RM": "Milieu droit",
    "LM": "Milieu gauche",
    "CAM": "Milieu offensif",
    "RW": "Ailier droit",
    "LW": "Ailier gauche",
    "ST": "Attaquant",
}
BASE_URL = "https://data-api.playerelo.football/v1"
