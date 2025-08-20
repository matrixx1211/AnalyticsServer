import os
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from models import db
from routes import api, env
from jobs import save_all_users, every_24_hours, pull_campaings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    # ------------------------------------------------------------------------------------------------ #
    """Inicializace aplikace"""
    # ------------------------------------------------------------------------------------------------ #
    app = Flask(__name__)  # Inicializace Flask aplikace
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, env['DATABASE_PATH'])}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(app, origins=["http://localhost", "https://localhost:4200"])  # Povolení CORS pro všechny domény

    scheduler = BackgroundScheduler(daemon=True)

    # Inicializace databáze v aplikaci
    db.init_app(app)

    # Registrace blueprintu pro API
    app.register_blueprint(api)

    # Inicializace databáze a vytvoření tabulek
    with app.app_context():
        db.create_all()
        # save_all_users()

    # scheduler.add_job(every_24_hours, "interval", args=[app], id="every_24_hours_job", replace_existing=True, minutes=1)

    # scheduler.add_job(save_all_users, "interval", args=[app], id="save_all_users_job", replace_existing=True, minutes=1)

    scheduler.add_job(
        pull_campaings, "interval", args=[app], id="pull_campaings_job", replace_existing=True, seconds=10
    )

    scheduler.start()

    return app


if __name__ == "__main__":  # Spuštění Flask aplikace pro vývoj
    app = create_app()
    app.run(debug=True)
