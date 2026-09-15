import re
import unicodedata
from difflib import SequenceMatcher

import requests

from constantes.constantes import API_KEY, BASE_URL


class PlayerEloError(RuntimeError):
    pass


def normaliser(texte: object) -> str:
    valeur = unicodedata.normalize("NFKD", str(texte or ""))
    valeur = "".join(
        caractere for caractere in valeur if not unicodedata.combining(caractere)
    )
    return " ".join(re.findall(r"[a-z0-9]+", valeur.casefold()))


def terme_recherche(nom: str) -> str:
    mots = normaliser(nom).split()
    mots_significatifs = [
        mot for mot in mots if mot not in {"jr", "junior", "ii", "iii"}
    ]
    return mots_significatifs[-1] if mots_significatifs else normaliser(nom)


def score_candidat(nom: str, equipe: str, candidat: dict) -> float:
    nom_local = normaliser(nom)
    nom_api = normaliser(candidat.get("player_name"))
    equipe_locale = normaliser(equipe)
    equipe_api = normaliser(candidat.get("current_team"))
    if not nom_api:
        return 0.0

    score = SequenceMatcher(None, nom_local, nom_api).ratio()
    mots_locaux = nom_local.split()
    mots_api = nom_api.split()
    if mots_locaux and mots_api and mots_locaux[-1] == mots_api[-1]:
        score += 0.18
    if mots_locaux and mots_api and mots_locaux[0][0] == mots_api[0][0]:
        score += 0.08
    if equipe_locale and equipe_api:
        score += 0.20 * SequenceMatcher(None, equipe_locale, equipe_api).ratio()
    return score


def choisir_candidat(
    nom: str, equipe: str, candidats: list[dict]
) -> tuple[dict | None, str]:
    candidats_valides = [
        candidat for candidat in candidats if candidat.get("player_id") is not None
    ]
    if not candidats_valides:
        return None, "introuvable"

    classement = sorted(
        (
            (score_candidat(nom, equipe, candidat), candidat)
            for candidat in candidats_valides
        ),
        key=lambda element: element[0],
        reverse=True,
    )
    meilleur_score, meilleur = classement[0]
    deuxieme_score = classement[1][0] if len(classement) > 1 else 0.0

    if meilleur_score < 0.78:
        return None, "score_insuffisant"
    if meilleur_score - deuxieme_score < 0.08:
        return None, "ambigu"
    return meilleur, "trouve"


def _creer_session(api_key: str) -> requests.Session:
    if not api_key.strip():
        raise PlayerEloError("La clé API Player ELO est absente.")
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {api_key}"})
    return session


def _appeler_api(
    session: requests.Session, endpoint: str, params: dict | None = None
) -> object:
    try:
        reponse = session.get(f"{BASE_URL}{endpoint}", params=params, timeout=30)
        reponse.raise_for_status()
        return reponse.json()
    except requests.HTTPError as erreur:
        code = erreur.response.status_code if erreur.response is not None else "inconnu"
        if code == 401:
            message = "Clé API Player ELO invalide ou absente."
        elif code == 429:
            message = "Limite de requêtes Player ELO atteinte. Réessayez plus tard."
        else:
            message = f"Player ELO a répondu avec l’erreur HTTP {code}."
        raise PlayerEloError(message) from erreur
    except (requests.RequestException, ValueError) as erreur:
        raise PlayerEloError(
            f"Impossible de contacter Player ELO : {erreur}"
        ) from erreur


def _extraire_joueurs(resultat: object) -> list[dict]:
    if isinstance(resultat, list):
        return [joueur for joueur in resultat if isinstance(joueur, dict)]
    if isinstance(resultat, dict):
        joueurs = resultat.get("players", resultat.get("data", []))
        if isinstance(joueurs, list):
            return [joueur for joueur in joueurs if isinstance(joueur, dict)]
    return []


def rechercher_joueur(
    nom: str,
    equipe: str,
    session: requests.Session | None = None,
) -> dict:
    """Recherche un joueur et retourne le candidat Player ELO le plus fiable."""
    client = session or _creer_session(API_KEY)
    resultat = _appeler_api(
        client,
        "/players",
        {"search": terme_recherche(nom), "limit": 100},
    )
    candidat, statut = choisir_candidat(nom, equipe, _extraire_joueurs(resultat))
    if candidat is None:
        raise PlayerEloError(
            f"Aucune correspondance fiable pour {nom} ({equipe}) : {statut}."
        )
    return candidat


def recuperer_valeur_par_id(
    player_id: int | str,
    session: requests.Session | None = None,
) -> dict:
    """Récupère la réponse de valeur marchande pour un ID Player ELO."""
    client = session or _creer_session(API_KEY)
    resultat = _appeler_api(client, f"/players/{player_id}/value")
    if not isinstance(resultat, dict):
        raise PlayerEloError("Format de valeur marchande inattendu.")
    return resultat


def extraire_valeur_marchande(resultat: dict) -> int | float | str | None:
    """Extrait le montant depuis les différentes formes de réponse possibles."""
    champs = (
        "market_value_eur",
        "estimated_value_eur",
        "value_eur",
        "market_value",
        "estimated_value",
        "value",
    )
    for champ in champs:
        valeur = resultat.get(champ)
        if isinstance(valeur, (int, float, str)) and not isinstance(valeur, bool):
            return valeur

    for valeur in resultat.values():
        if isinstance(valeur, dict):
            montant = extraire_valeur_marchande(valeur)
            if montant is not None:
                return montant
    return None


def recuperer_joueur_et_valeur(nom: str, equipe: str) -> dict:
    """Résout l’ID puis récupère la valeur marchande en deux requêtes API."""
    session = _creer_session(API_KEY)
    joueur = rechercher_joueur(nom, equipe, session)
    reponse_valeur = recuperer_valeur_par_id(joueur["player_id"], session)
    return {
        "player_id": joueur["player_id"],
        "player_name": joueur.get("player_name", nom),
        "current_team": joueur.get("current_team", equipe),
        "market_value": extraire_valeur_marchande(reponse_valeur),
        "value_details": reponse_valeur,
    }
