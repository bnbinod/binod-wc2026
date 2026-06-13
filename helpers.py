import re
import requests

from models import Game, Team


def _sort_by_id(dict_list, column_name='id'):
    def _id_key(item):
        val = item.get(column_name, 0)
        if isinstance(val, int):
            return val
        try:
            return int(val)
        except Exception:
            try:
                m = re.search(r"-?\d+", str(val))
                if m:
                    return int(m.group())
            except Exception:
                pass
        return 0

    try:
        dict_list.sort(key=_id_key)
    except Exception:
        pass
    return dict_list


def game_outcomes():
    games = Game.query.all()
    outcomes = {}
    for game in games:
        if game.finished and isinstance(game.finished, str) and game.finished.strip().lower() == 'true':
            outcomes[game.id] = game.winner_iso
    return outcomes


def fetch_game_outcomes():
    """
    Return the key value pairs of the game output as a dict with keys as match ids and values as the winner's ISO code (or "DRW" for draw).

    Returns:
    dictionary
    """
    url = "https://worldcup26.ir/get/games"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        payload = {}

    if isinstance(payload, list):
        dict_results = payload
    elif isinstance(payload, dict):
        if "games" in payload and isinstance(payload["games"], list):
            dict_results = payload["games"]
        elif "data" in payload and isinstance(payload["data"], list):
            dict_results = payload["data"]
        else:
            dict_results = [payload]
    else:
        dict_results = []

    teams = team_codes()
    results = {}

    for row in dict_results:
        if row.get('time_elapsed') != 'finished':
            continue

        home_score = row.get('home_score', 0)
        away_score = row.get('away_score', 0)
        winner_iso = ''
        if home_score < away_score:
            winner_iso = teams.get(int(row.get('away_team_id')))
        elif home_score > away_score:
            winner_iso = teams.get(int(row.get('home_team_id')))
        else:
            winner_iso = "DRW"

        match_id = row.get('id')
        if match_id is not None:
            results[int(match_id)] = winner_iso

    return results


def team_codes():
    teams = Team.query.all()
    return {team.id: team.fifa_code for team in teams}
