import os
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from models import db
from routes import api
from jobs import every_24_hours
from utils import startup_actions, get_posts_metrics
from config import Config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    # ------------------------------------------------------------------------------------------------ #
    """Inicializace aplikace"""
    # ------------------------------------------------------------------------------------------------ #
    app = Flask(__name__)  # Inicializace Flask aplikace
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, Config.DATABASE_PATH)}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Povolení CORS pro všechny domény
    CORS(
        app,
        origins=[
            "http://localhost:4200",
            "https://localhost:4200",
            "https://creators.contentbox.cz",
            "https://beautynews.loreal.cz",
        ],
    )

    # Inicializace databáze v aplikaci
    db.init_app(app)

    # Registrace blueprintu pro API
    app.register_blueprint(api)

    # Inicializace databáze a vytvoření tabulek
    flask_app_context = app.app_context()
    with flask_app_context:
        db.create_all()

    # Akce, které se provedou na začátku
    # """ TODO: ODKOMENTOVAT """
    startup_actions(flask_app_context)
    # get_posts_metrics(flask_app_context)

    # Inicializace plánovače
    scheduler = BackgroundScheduler(daemon=True)

    scheduler.add_job(
        every_24_hours, "interval", args=[flask_app_context], id="every_24_hours_job", replace_existing=True, hours=24
    )

    scheduler.start()

    return app


if __name__ == "__main__":  # Spuštění Flask aplikace pro vývoj
    app = create_app()
    app.run(debug=True)
