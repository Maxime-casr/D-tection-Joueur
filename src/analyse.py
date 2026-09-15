from pathlib import Path

import pandas as pd
import streamlit as st

COLONNES_REQUISES = {
    "Name",
    "Team",
    "League",
    "Position",
    "Age",
    "Nation",
    "gender",
    "OVR",
    "PAC",
    "SHO",
    "PAS",
    "DRI",
    "DEF",
    "PHY",
}


@st.cache_data(show_spinner="Chargement des joueurs...")
def charger_donnees(chemin: Path) -> pd.DataFrame:
    df = pd.read_csv(chemin)
    colonnes_manquantes = COLONNES_REQUISES.difference(df.columns)
    if colonnes_manquantes:
        liste_colonnes = ", ".join(sorted(colonnes_manquantes))
        raise ValueError(f"Colonnes absentes du dataset : {liste_colonnes}")
    return df
