import pandas as pd
import streamlit as st

from src.playerelo import PlayerEloError, recuperer_joueur_et_valeur


def _formater_valeur_marchande(valeur: object) -> str:
    if isinstance(valeur, (int, float)) and not isinstance(valeur, bool):
        return f"{valeur:,.0f} €".replace(",", " ")
    return str(valeur) if valeur not in (None, "") else "Non disponible"


@st.dialog(
    "Valeur marchande",
    icon=":material/euro:",
    on_dismiss="rerun",
)
def afficher_valeur_marchande(nom: str, equipe: str) -> None:
    st.caption(f"{nom} · {equipe}")
    cache = st.session_state.setdefault("valeurs_marchandes", {})
    cle_cache = f"{nom}|{equipe}"

    if cle_cache not in cache:
        with st.spinner("Recherche du joueur et de sa valeur..."):
            try:
                cache[cle_cache] = recuperer_joueur_et_valeur(nom, equipe)
            except PlayerEloError as erreur:
                st.error(str(erreur), icon=":material/error:")
                return

    resultat = cache[cle_cache]
    st.metric(
        "Valeur marchande estimée(Player ELO)",
        _formater_valeur_marchande(resultat.get("market_value")),
        border=True,
    )
    st.caption(
        f"Correspondance API : {resultat.get('player_name', nom)} · "
        f"ID {resultat.get('player_id', 'inconnu')}"
    )
    if resultat.get("market_value") is None:
        st.warning(
            "L’API n’a pas renvoyé de montant identifiable. La réponse brute est affichée ci-dessous."
        )
        st.json(resultat.get("value_details", {}), expanded=True)


def memoriser_joueur_valeur(profils: pd.DataFrame) -> None:
    clic = st.session_state.get("clic_valeur_marchande")
    if clic is None:
        return
    index = int(clic["row"])
    if 0 <= index < len(profils):
        ligne = profils.iloc[index]
        st.session_state["joueur_valeur_selectionne"] = {
            "nom": ligne["Joueur"],
            "equipe": ligne["Équipe"],
        }
