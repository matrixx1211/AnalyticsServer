from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from models import db
from routes import api, env
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import logging

jobs_logger = logging.getLogger("SchedulerJobs")
jobs_logger.setLevel(logging.INFO)


def run():
    # ------------------------------------------------------------------------------------------------ #
    """Konfigurace"""
    # ------------------------------------------------------------------------------------------------ #
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    app = Flask(__name__)  # Inicializace Flask aplikace
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{os.path.join(BASE_DIR, env['DATABASE_PATH'])}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    CORS(
        app, origins=["http://localhost", "https://localhost:4200"]
    )  # Povolení CORS pro všechny domény

    # ------------------------------------------------------------------------------------------------ #
    """                                           Databáze                                           """
    # ------------------------------------------------------------------------------------------------ #
    db.init_app(app)  # Inicializace databáze v aplikaci

    # ------------------------------------------------------------------------------------------------ #
    """                                           API cesty                                          """
    # ------------------------------------------------------------------------------------------------ #
    app.register_blueprint(api)  # Registrace blueprintu pro API

    with app.app_context():  # Inicializace databáze a vytvoření tabulek
        db.create_all()

    scheduler = BackgroundScheduler(
        {
            "apscheduler.jobstores.default": {
                "type": "sqlalchemy",
                "url": "sqlite:///analytics.db",
            },
            "apscheduler.executors.default": {
                "class": "apscheduler.executors.pool:ThreadPoolExecutor",
                "max_workers": "1",
            },
            "apscheduler.executors.processpool": {
                "type": "processpool",
                "max_workers": "1",
            },
            "apscheduler.job_defaults.coalesce": "false",
            "apscheduler.job_defaults.max_instances": "1",
            "apscheduler.timezone": "UTC",
        }
    )

    scheduler.add_job(
        func=every_24_hours,
        trigger="interval",
        minutes=1,
        id="my_job_id",
        replace_existing=True,
    )
    scheduler.start()  # Spuštění plánovače úloh

    return app


def every_24_hours():
    jobs_logger.info(f"This job runs every 24 hours {datetime.datetime.now()}")
    print(f"This job runs every 24 hours {datetime.datetime.now()}")


if __name__ == "__main__":  # Spuštění Flask aplikace pro vývoj
    run().run(debug=True)
