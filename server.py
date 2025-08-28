import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

from models import db
from routes import api, dev
from jobs import every_24_hours
from utils import startup_actions
from config import Config


def create_app():
    # ------------------------------------------------------------------------------------------------ #
    """Inicializace aplikace"""
    # ------------------------------------------------------------------------------------------------ #
    # inicializace .env
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    # nastavení a vytvoření Flask aplikace
    app = Flask(__name__)  # Inicializace Flask aplikace
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, Config.DATABASE_PATH)}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Povolení CORS pro všechny domény
    if not Config.DEV:
        CORS(app, origins=Config.CORS)
    else:
        CORS(app)

    # Inicializace databáze v aplikaci
    db.init_app(app)

    # Registrace blueprintů pro API
    app.register_blueprint(api)
    app.register_blueprint(dev)  # TODO: toto odstranit následně pro produkci

    # Inicializace databáze a vytvoření tabulek
    flask_app_context = app.app_context()
    with flask_app_context:
        db.create_all()

    # Akce, které se provedou na začátku
    startup_actions(flask_app_context)

    # Inicializace plánovače
    scheduler = BackgroundScheduler(daemon=True)

    """ Pro produkci určitě nastavit na 24h """
    scheduler.add_job(
        every_24_hours,
        "interval",
        args=[flask_app_context],
        id="every_24_hours_job",
        replace_existing=True,
        # hours=24
        minutes=10,
    )

    scheduler.start()

    return app


if __name__ == "__main__":  # Spuštění Flask aplikace pro vývoj
    app = create_app()
    app.run(debug=True)
