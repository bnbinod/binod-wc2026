import requests
import streamlit as st
import pandas as pd
from flask import Flask

from models import db, Team, Game, Staff, Prediction


def create_app():
    mysql = st.secrets["mysql"]
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql['user']}:{mysql['password']}@"
        f"{mysql['host']}:{mysql.get('port', 3306)}/{mysql['db']}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


APP = create_app()


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Binod WorldCup 2026: Prediction Results',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)


@st.cache_data
def get_team_codes():
    codes = {}
    with APP.app_context():
        teams = Team.query.all()
        for team in teams:
            try:
                codes[int(team.id)] = team.fifa_code
            except Exception:
                # skip malformed entries
                continue

    return codes

st.header(f'Binod WorldCup 2026: Prediction Standings', divider='gray')

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


@st.cache_data
def get_games_from_db():
    """Read games from the local SQLite DB and return a list of dicts suitable for
    displaying with `st.dataframe()`.

    Columns returned: id, home_team_iso, away_team_iso, home_score, away_score,
    winner_iso, finished, date_time, type
    """
    rows = []
    with APP.app_context():
        games = Game.query.all()
        for g in games:
            try:
                rows.append({
                    'id': g.id,
                    'home_team_iso': g.home_team_iso,
                    'away_team_iso': g.away_team_iso,
                    'home_score': g.home_score,
                    'away_score': g.away_score,
                    'winner_iso': g.winner_iso,
                    'finished': g.finished,
                    'date_time': g.date_time,
                    'type': g.type,
                })
            except Exception:
                continue

    return rows


@st.cache_data
def get_staffs_from_db():
    """Read staff rows from the local SQLite DB and return a pandas DataFrame."""
    rows = []
    with APP.app_context():
        staffs = Staff.query.all()
        for s in staffs:
            try:
                rows.append({
                    'id': s.id,
                    'staff_code': s.staff_code,
                    'staff_name': s.staff_name,
                })
            except Exception:
                continue

    return pd.DataFrame(rows)


@st.cache_data
def get_leaderboard_from_db():
    """Build a leaderboard DataFrame from Prediction results and match outputs."""
    with APP.app_context():
        rows = Prediction.query.with_entities(
            Prediction.match_number,
            Prediction.staff_code,
            Prediction.prediction_iso
        ).all()

    df = pd.DataFrame(rows, columns=['match_number', 'staff_code', 'prediction_iso'])
    # Build the actual game outputs from the DB or external API.
    game_output = get_games()

    pivot_df = df.pivot_table(
        index='match_number',
        columns='staff_code',
        values='prediction_iso',
        aggfunc='first'
    )

    dict_results = pivot_df.reset_index().to_dict(orient='records')

    for row in dict_results:
        match_output = game_output.get(int(row['match_number']))
        if match_output is None:
            continue

        for key, value in list(row.items()):
            if key == 'match_number':
                continue

            if value is None or (isinstance(value, float) and pd.isna(value)):
                row[key] = ''
            elif isinstance(value, str):
                predicted_output = value.strip()
                if predicted_output == 'DRW' and match_output == 'DRW':
                    row[key] = 'DRW (2)'
                elif predicted_output == match_output:
                    row[key] = value + ' (1)'
                else:
                    row[key] = value + ' (0)'

    return pd.DataFrame(dict_results)

teams = get_team_codes()
st.subheader('Teams')
st.dataframe(teams, use_container_width=True, hide_index=True)

# Also show games read from the local database
try:
    db_games = get_games_from_db()
    if db_games:
        st.subheader('Games')
        st.dataframe(db_games, use_container_width=True, hide_index=True)
    else:
        st.info('No games found in database.')
except Exception as e:
    st.error(f'Error reading games from DB: {e}')

# Show staff from the local database
try:
    staff_df = get_staffs_from_db()
    if not staff_df.empty:
        st.subheader('Staffs')
        st.dataframe(staff_df, use_container_width=True, hide_index=True)
    else:
        st.info('No staff records found in database.')
except Exception as e:
    st.error(f'Error reading staff from DB: {e}')


# Leaderboard section (predictions outcomes per staff)
try:
    leaderboard_df = get_leaderboard_from_db()
    if not leaderboard_df.empty:
        st.subheader('Leaderboard')
        st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
    else:
        st.info('No leaderboard data available.')
except Exception as e:
    st.error(f'Error building leaderboard from DB: {e}')


# app = Flask(__name__)

# db_path = os.path.join(app.root_path, "mydb.db")
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db.init_app(app)
# app.register_blueprint(main_bp)

# if __name__ == "__main__":
#     app.run(debug=False)
#     # app.run(debug=True)









