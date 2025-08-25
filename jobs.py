import logging
from requests import get
from datetime import datetime, timedelta
from utils import startup_actions

from config import Config

jobs_logger = logging.getLogger("ScheduledJobs")
jobs_logger.setLevel(logging.INFO)

if Config.DEV:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s - %(message)s"))

    jobs_logger.addHandler(handler)


def every_24_hours(app_context):
    jobs_logger.info(f"Starting job, that runs every 24 hours. Now: {datetime.now()}")

    with app_context:
        # Dělám to stejné, co na začátku při spuštění
        startup_actions(app_context)

        # Vyřešit metriky účtu
        # get_

        # Vyřešit metriky příspěvků
