import logging
from requests import get
from datetime import datetime, timedelta

from config import Config
from models import Users, db, Campaigns, CampaignUsers

jobs_logger = logging.getLogger("SchedulerJobs")
jobs_logger.setLevel(logging.INFO)

if Config.DEV:

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s - %(message)s"))

    jobs_logger.addHandler(handler)


def save_all_users(app_context):
    with app_context:
        response = get(Config.CREATORS_API_URL + "/api-influencers/creators/")
        data = response.json()
        creators = data.get("creators")

        if len(creators) == 0:
            jobs_logger.info("No creators found.")
            return

        for creator in creators:
            jobs_logger.info(f"Saving creator: {creator.get('email')}")

            if Users.query.filter_by(creators_email=creator.get("email")).one_or_none():
                jobs_logger.info(f"Creator {creator.get('email')} already exists, skipping.")
                continue

            db.session.add(Users(creators_id=creator.get("id"), creators_email=creator.get("email")))

        db.session.commit()


def pull_campaings(app_context):
    with app_context:
        # Načtu všechny kampaně
        response = get(Config.CREATORS_API_URL + "/api-influencers/campaigns/")
        data = response.json()
        campaigns = data.get("campaigns")

        # Pokud nejsou kampaně, tak skončím
        if len(campaigns) == 0:
            jobs_logger.info("No campaigns found.")
            return []

        # Pro každou kampaň procházím a zjištuji:
        for campaign in campaigns:
            # Datum publikování kampaně je povinné
            if campaign.get("publishing_start_date") is None or campaign.get("publishing_end_date") is None:
                jobs_logger.info(f"Campaign {campaign.get('id')} has no start or end date, skipping.")
                continue

            start_date = datetime.strptime(campaign.get("publishing_start_date"), "%Y-%m-%d").date()
            end_date = datetime.strptime(campaign.get("publishing_end_date"), "%Y-%m-%d").date() + timedelta(days=14)

            # zkontroluji, zda už kampaň není uložená v DB
            if Campaigns.query.filter_by(creators_id=campaign.get("id")).one_or_none():
                jobs_logger.info(f"Campaign {campaign.get('name')} ({campaign.get('id')}) already exists, skipping.")
                continue

            # Pokud ne, tak ji uložím
            jobs_logger.info(f"Saving campaign: {campaign.get('name')} ({campaign.get('id')})")
            db.session.add(
                Campaigns(
                    creators_id=campaign.get("id"),
                    name=campaign.get("name"),
                    hashtags=campaign.get("hashtags"),
                    instagram_reel=campaign.get("instagram_reel", False),
                    instagram_post=campaign.get("instagram_post", False),
                    instagram_story=campaign.get("instagram_story", False),
                    tiktok_video=campaign.get("tiktok_video", False),
                    facebook_posts=campaign.get("facebook_posts", False),
                    start_date=start_date,
                    end_date=end_date,
                )
            )

        db.session.commit()

        return campaigns


def campaign_users(app_context, ids):
    with app_context:
        # Načtu všechny kampaně
        response = get(Config.CREATORS_API_URL + "/api-influencers/involved?campaign-ids=" + str(ids))
        data = response.json()
        if not data or len(data) == 0:
            jobs_logger.info(f"No data sent, skipping.")
            return

        # Projdu všechny kampaně a k nim všechny uživatele
        for current in data:
            campaign_id = current.get("campaign_id")
            creator_ids = current.get("creator_ids")

            for creator_id in creator_ids:
                # Pokud už daná kombinace existuje, tak nepřidávám
                if CampaignUsers.query.filter_by(campaign_id=campaign_id, user_id=creator_id).one_or_none():
                    jobs_logger.info(
                        f"Record with user ID {creator_id} and campaign ID {campaign_id} already exists, skipping."
                    )
                    continue

                # Jinak přidám
                db.session.add(CampaignUsers(campaign_id=campaign_id, user_id=creator_id))
                jobs_logger.info(f"Saving record with user ID {creator_id} and campaign ID {campaign_id}.")

        db.session.commit()


def every_24_hours(app_context):
    jobs_logger.info(f"Starting job, that runs every 24 hours. Now: {datetime.now()}")

    with app_context:
        # Dělám to stejné, co na začátku při spuštění
        campaigns = pull_campaings(app_context)
        save_all_users(app_context)
        ids = []
        for campaign in campaigns:
            ids.append(campaign.get("id"))

        campaign_users(app_context, ids)

        # Vyřešit metriky účtu

        # Vyřešit metriky příspěvků
