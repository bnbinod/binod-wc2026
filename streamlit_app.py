import requests
import streamlit as st
import os
from flask import Flask

from models import db, Team


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)


@st.cache_data
def get_team_codes():
    # Use the application's SQLite database for team codes.
    # Ensure DB is initialized and use an application context when querying.
    db_path = os.path.join(os.path.dirname(__file__), "mydb.db")
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    codes = {}
    with app.app_context():
        teams = Team.query.all()
        for team in teams:
            try:
                codes[int(team.id)] = team.fifa_code
            except Exception:
                # skip malformed entries
                continue

    return codes

st.header(f'WC 2026 ', divider='gray')

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_games():
    
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

    teams = get_team_codes()
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

# game_outcomes = get_games()

game_outcomes = get_team_codes()
st.dataframe(game_outcomes, use_container_width=True, hide_index=True)


# app = Flask(__name__)

# db_path = os.path.join(app.root_path, "mydb.db")
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db.init_app(app)
# app.register_blueprint(main_bp)

# if __name__ == "__main__":
#     app.run(debug=False)
#     # app.run(debug=True)









