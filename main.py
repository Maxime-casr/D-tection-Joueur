import streamlit as st

from app import lancer_app
from constantes.constantes import DATA_PATH
from src.analyse import charger_donnees


def main():
    st.set_page_config(
        page_title="Détection football",
        page_icon=":material/person_search:",
        layout="wide",
        initial_sidebar_state="auto",
    )
    try:
        df = charger_donnees(DATA_PATH)
    except (FileNotFoundError, ValueError) as erreur:
        st.error(f"Impossible de charger les données : {erreur}")
        st.stop()
    lancer_app(df)


if __name__ == "__main__":
    main()
