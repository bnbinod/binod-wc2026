from flask import Blueprint, render_template, request, redirect
from sqlalchemy import func
import requests
import pandas as pd

from models import db, Game, Team, Staff, Prediction
from helpers import _sort_by_id, game_outcomes, team_codes

main_bp = Blueprint('main', __name__)

@main_bp.route('/staffs', methods=['GET', 'POST'])
def get_staffs():
    staffs = Staff.query.all()
    SKIP_COLUMNS = {'id'}
    dict_results = [
        {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in SKIP_COLUMNS}
        for row in staffs
    ]
    return render_template('list_data.html', data=dict_results, title='Staffs')

#-- Used as countries
@main_bp.route('/teams', methods=['GET'])
def get_teams():
    teams = Team.query.all()
    SKIP_COLUMNS = set()
    dict_results = [
        {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in SKIP_COLUMNS}
        for row in teams
    ]
    return render_template('list_data.html', data=dict_results, title='Teams')


@main_bp.route('/games', methods=['GET'])
def get_matches():
    matches = Game.query.all()
    SKIP_COLUMNS = {}
    dict_results = [
        {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in SKIP_COLUMNS}
        for row in matches
    ]

    return render_template('list_data.html', data=dict_results, title='Matches')


@main_bp.route('/predictions', methods=['GET'])
def get_predictions():
    predictions = (
        db.session.query(Prediction, Staff.staff_name.label('staff_name'))
        .outerjoin(Staff, Prediction.staff_code == Staff.staff_code)
        .all()
    )
    SKIP_COLUMNS = {'id'}
    dict_results = []
    for row, staff_name in predictions:
        row_dict = {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in SKIP_COLUMNS}
        row_dict['staff_name'] = staff_name
        dict_results.append(row_dict)
    return render_template('list_data.html', data=dict_results, title="Staff's Predictions")


@main_bp.route('/leaderboard', methods=['GET'])
def pivot():
    rows = Prediction.query.with_entities(
        Prediction.match_number,
        Prediction.staff_code,
        Prediction.prediction_iso
    ).all()

    df = pd.DataFrame(rows, columns=['match_number', 'staff_code', 'prediction_iso'])
    game_output = game_outcomes()
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

    _sort_by_id(dict_results, 'match_number')
    return render_template('predictions.html', data=dict_results, title='Predictions')


@main_bp.route('/live', methods=['GET'])
def get_live():
    predictions = (
        db.session.query(Prediction, Staff.staff_name.label('staff_name'))
        .outerjoin(Staff, Prediction.staff_code == Staff.staff_code)
        .all()
    )
    SKIP_COLUMNS = {'id'}
    dict_results = []
    for row, staff_name in predictions:
        row_dict = {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in SKIP_COLUMNS}
        row_dict['staff_name'] = staff_name
        dict_results.append(row_dict)
    return render_template('list_data.html', data=dict_results, title="Staff's Predictions")


@main_bp.route('/teams_api', methods=['GET'])
def get_teams_api():
    url = 'https://worldcup26.ir/get/teams'
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        payload = {}

    if isinstance(payload, list):
        dict_results = payload
    elif isinstance(payload, dict):
        if 'teams' in payload and isinstance(payload['teams'], list):
            dict_results = payload['teams']
        elif 'data' in payload and isinstance(payload['data'], list):
            dict_results = payload['data']
        else:
            dict_results = [payload]
    else:
        dict_results = []

    _sort_by_id(dict_results)
    return render_template('teams.html', rows=dict_results, title='Teams')


@main_bp.route('/fetch_games', methods=['GET'])
def get_games():
    url = 'https://worldcup26.ir/get/games'
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        payload = {}

    if isinstance(payload, list):
        dict_results = payload
    elif isinstance(payload, dict):
        if 'games' in payload and isinstance(payload['games'], list):
            dict_results = payload['games']
        elif 'data' in payload and isinstance(payload['data'], list):
            dict_results = payload['data']
        else:
            dict_results = [payload]
    else:
        dict_results = []

    _sort_by_id(dict_results)
    return render_template('list_data.html', data=dict_results, title='Games')


@main_bp.route('/staff_scores', methods=['GET'])
def get_staff_scores():
    rows = db.session.query(
        Prediction.staff_code,
        func.coalesce(func.sum(Prediction.predictor_score), 0).label('total_score')
    ).group_by(Prediction.staff_code).all()

    dict_results = [
        {'staff_code': r[0], 'total_score': int(r[1]) if r[1] is not None else 0}
        for r in rows
    ]
    return render_template('list_data.html', data=dict_results, title='Staff Scores')
