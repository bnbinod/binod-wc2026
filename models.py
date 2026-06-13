from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Staff(db.Model):
    # This explicit string becomes the database table name
    __tablename__ = "staffs" 
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    staff_code = db.Column(db.String(10))
    staff_name = db.Column(db.String(200))

class Prediction(db.Model):
    # This explicit string becomes the database table name
    __tablename__ = "predictions" 
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    match_number = db.Column(db.Integer)
    staff_code = db.Column(db.String(10))
    staff = db.Column(db.String(200))
    prediction_iso = db.Column(db.String(10))
    prediction = db.Column(db.String(50))
    # predictor_score = db.Column(db.Integer)
    game = db.Column(db.String(200))

# class Match(db.Model):
#     # This explicit string becomes the database table name
#     __tablename__ = "matches" 
#     id = db.Column(db.Integer,primary_key=True, autoincrement=True)
#     match_number = db.Column(db.Integer)
#     team1_iso = db.Column(db.String(10))
#     team2_iso = db.Column(db.String(10))
#     team1_score = db.Column(db.Integer)
#     team2_score = db.Column(db.Integer)
#     output = db.Column(db.String(200))
#     game_full_name = db.Column(db.String(200))

class Game(db.Model):
    # This explicit string becomes the database table name
    __tablename__ = "games" 
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    away_team_id = db.Column(db.Integer)
    home_team_id = db.Column(db.Integer)
    away_team_iso = db.Column(db.String(5))
    home_team_iso = db.Column(db.String(5))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    winner_iso = db.Column(db.String(5))
    finished = db.Column(db.String(5))
    date_time = db.Column(db.String(20))
    type = db.Column(db.String(20))

class Country(db.Model):
    # This explicit string becomes the database table name
    __tablename__ = "countries" 
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    FIFA_Code = db.Column(db.String(5))
    name = db.Column(db.String(100))

class Team(db.Model):
    # This explicit string becomes the database table name
    __tablename__ = "teams" 
    id = db.Column(db.Integer,primary_key=True, autoincrement=True)
    fifa_code = db.Column(db.String(10))
    country = db.Column(db.String(100))
    group = db.Column(db.String(2))
