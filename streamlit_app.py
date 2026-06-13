import os
from flask import Flask

from models import db
from routes import main_bp

app = Flask(__name__)

db_path = os.path.join(app.root_path, "mydb.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
