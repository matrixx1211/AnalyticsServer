import re
import logging
from requests import get, post
from config import Config
from models import Users, db, Campaigns, CampaignUsers, Posts
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from dateutil import parser

utils_logger = logging.getLogger("Utils")
utils_logger.setLevel(logging.INFO)

if Config.DEV:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s - %(message)s"))

    utils_logger.addHandler(handler)


def save_all_users(app_context):
    with app_context:
        response = get(Config.CREATORS_API_URL + "/api-influencers/creators/")
        data = response.json()
        creators = data.get("creators")

        if len(creators) == 0:
            utils_logger.info("No creators found.")
            return

        for creator in creators:
            utils_logger.info(f"Saving creator: {creator.get('email')}")

            if Users.query.filter_by(creators_email=creator.get("email")).one_or_none():
                utils_logger.info(f"Creator {creator.get('email')} already exists, skipping.")
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
            utils_logger.info("No campaigns found.")
            return []

        # Pro každou kampaň procházím a zjištuji:
        for campaign in campaigns:
            # Nejdůležitější je hashtag, tzn. není -> nezajímá mě
            if not campaign["hashtags"]:
                utils_logger.info(f"Campaign {campaign['name']} ({campaign['id']}) has no hashtags, skipping.")
                continue

            # Datum publikování kampaně je povinné
            if campaign["publishing_start_date"] is None or campaign["publishing_end_date"] is None:
                utils_logger.info(f"Campaign {campaign['name']} ({campaign['id']}) has no start or end date, skipping.")
                continue

            start_date = datetime.strptime(campaign.get("publishing_start_date"), "%Y-%m-%d").date()
            end_date = datetime.strptime(campaign.get("publishing_end_date"), "%Y-%m-%d").date() + timedelta(days=14)

            # IG post = 1, IG story = 2, IG reel = 3, TT video = 4, FB post = _ (nevím)
            platforms = {"igp": False, "igs": False, "igr": False, "ttv": False, "fbp": False}
            for platform in campaign["platforms"]:
                platform_id = platform["id"]
                match platform_id:
                    case 1:
                        platforms["igp"] = True
                    case 2:
                        platforms["igs"] = True
                    case 3:
                        platforms["igr"] = True
                    case 4:
                        platforms["ttv"] = True
                    case _:
                        platforms["fbp"] = True

            # zkontroluji, zda už kampaň není uložená v DB, pokud je, tak upravím pouze data
            current_campaign = Campaigns.query.filter_by(creators_id=campaign["id"])
            if current_campaign.one_or_none():
                utils_logger.info(f"Campaign {campaign['name']} ({campaign['id']}) already exists, updating.")
                current_campaign.update(
                    {
                        "name": campaign["name"],
                        "hashtags": campaign["hashtags"],
                        "instagram_reel": platforms["igr"],
                        "instagram_post": platforms["igp"],
                        "instagram_story": platforms["igs"],
                        "tiktok_video": platforms["ttv"],
                        "facebook_post": platforms["fbp"],
                        "start_date": start_date,
                        "end_date": end_date,
                    }
                )
                continue

            # Pokud ne, tak ji uložím
            utils_logger.info(f"Saving campaign: {campaign.get('name')} ({campaign.get('id')})")
            db.session.add(
                Campaigns(
                    creators_id=campaign["id"],
                    name=campaign["name"],
                    hashtags=campaign["hashtags"],
                    instagram_reel=platforms["igr"],
                    instagram_post=platforms["igp"],
                    instagram_story=platforms["igs"],
                    tiktok_video=platforms["ttv"],
                    facebook_post=platforms["fbp"],
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
            utils_logger.info(f"No data sent, skipping.")
            return

        # Projdu všechny kampaně a k nim všechny uživatele
        for current in data:
            campaign_id = current.get("campaign_id")
            creator_ids = current.get("creator_ids")

            for creator_id in creator_ids:
                # Pokud už daná kombinace existuje, tak nepřidávám
                if CampaignUsers.query.filter_by(campaign_id=campaign_id, user_id=creator_id).one_or_none():
                    utils_logger.info(
                        f"Record with user ID {creator_id} and campaign ID {campaign_id} already exists, skipping."
                    )
                    continue

                # Jinak přidám
                db.session.add(CampaignUsers(campaign_id=campaign_id, user_id=creator_id))
                utils_logger.info(f"Saving record with user ID {creator_id} and campaign ID {campaign_id}.")

        db.session.commit()


def update_user(data):
    # Uživatel, kde email je zadaný email
    user = Users.query.filter_by(creators_email=data["creators_email"])

    # Pokud není uživatel, tak by měl být
    if not user.one_or_none():
        return False

    # Pokud je uživatel, tak ho aktualizuji
    user.update(values={key: value for key, value in data.items() if value is not None})
    db.session.commit()

    return True


def get_profile_metrics(email):
    # získání metrik pro uživatele a následně je uložím do DB
    user = Users.query.filter_by(creators_email=email)
    # get_instagram_metrics()
    # get_tiktok_metrics()


def get_posts_metrics(app_context):
    # získání metrik pro příspěvky a následně je uložím do DB
    # TODO: zde přidat ještě or_(and_(), ended) pro ty starší kampaně, pro které nebylo zatím nic vyhledáno
    """or_(
        and_(
            Campaigns.start_date <= datetime.now(),
            Campaigns.end_date >= datetime.now()
        ),
        Campaigns.ended == False
    )"""
    with app_context:
        campaigns = Campaigns.query.filter(
            and_(Campaigns.start_date <= datetime.now(), Campaigns.end_date >= datetime.now())
        ).all()

        # pro všechny kampaně
        for campaign in campaigns:
            # najdu / získání uživatelů, kteří jsou registrování v kampani
            campaign_users = CampaignUsers.query.filter_by(campaign_id=campaign.id).all()

            # pro všechny uživatele z kampaně vyhledávám ve všech příspěvcích postupně na platformách
            for campaign_user in campaign_users:
                user_query = Users.query.filter_by(id=campaign_user.user_id)
                user = user_query.first()

                # získání dat z IG
                if campaign.instagram_reel or campaign.instagram_post:
                    # získání dat o IG reels a IG posts
                    # {{baseFBURL}}/v23.0/ig_user_id?fields=business_discovery.username(ig_username){followers_count,media_count,media{like_count,comments_count,permalink,thumbnail_url,timestamp,view_count}}&access_token=token
                    instagram_content_request = get(
                        f"{Config.META_API_URL}/{user.instagram_user_id}/?fields=business_discovery.username({user.instagram_username}){{followers_count,media_count,media{{like_count,comments_count,permalink,thumbnail_url,timestamp,view_count,media_product_type,caption}}}}&access_token={user.meta_token}"
                    )

                    instagram_content = instagram_content_request.json()["business_discovery"]["media"]["data"]
                    if len(instagram_content) > 0:
                        for instagram_post in instagram_content:
                            # kontrola, jestli náhodou příspěvek již neexistuje
                            post_query = Posts.query.filter_by(platform_id=instagram_post.get("id"))

                            # pokud již existuje, tak pouze aktualizuji data
                            if post_query.one_or_none():
                                post_query.update(
                                    {
                                        "views": instagram_post.get("view_count", None),
                                        "likes": instagram_post.get("like_count", None),
                                        "comments": instagram_post.get("comments_count", None),
                                        "engagement_rate": (
                                            0
                                            if instagram_post.get("view_count", None) == 0
                                            or instagram_post.get("view_count", None) == None
                                            else (
                                                (
                                                    instagram_post.get("like_count", None)
                                                    + instagram_post.get("comments_count", None)
                                                )
                                                / instagram_post.get("view_count", None)
                                                * 100
                                            )
                                        ),
                                    }
                                )
                                continue

                            # IG post = 1, IG story = 2, IG reel = 3, TT video = 4, FB post = _ (nevím)
                            post_hashtags = set(re.findall(r"#(\w+)", instagram_post.get("caption")))
                            campaign_hashtags = set(campaign.hashtags.split(","))

                            if post_hashtags == campaign_hashtags:
                                platform_type_id = 1 if instagram_post["media_product_type"] == "FEED" else 3
                                db.session.add(
                                    Posts(
                                        platform_id=instagram_post.get("id"),
                                        platform_type_id=platform_type_id,
                                        published_at=parser.parse(instagram_post.get("timestamp", None)),
                                        media_url=instagram_post.get("permalink", None),
                                        thumbnail_url=instagram_post.get("thumbnail_url", None),
                                        views=instagram_post.get("view_count", None),
                                        likes=instagram_post.get("like_count", None),
                                        comments=instagram_post.get("comments_count", None),
                                        engagement_rate=(
                                            0
                                            if instagram_post.get("view_count", None) == 0
                                            or instagram_post.get("view_count", None) == None
                                            else (
                                                (
                                                    instagram_post.get("like_count", None)
                                                    + instagram_post.get("comments_count", None)
                                                )
                                                / instagram_post.get("view_count", None)
                                                * 100
                                            )
                                        ),
                                        user_id=user.id,
                                        campaign_id=campaign.id,
                                    )
                                )

                # získání dat o IG story
                # {{baseFBURL}}/ig_user_id/stories?access_token=token&fields=id,permalink,media_type,timestamp,thumbnail_url,like_count,comments_count
                """ if campaign.instagram_story:
                    instagram_stories_request = get(
                        f"{Config.META_API_URL}/{user.instagram_user_id}/stories?fields=fields=id,permalink,media_type,timestamp,thumbnail_url,like_count,comments_count&access_token={user.meta_token}"
                    )

                    instagram_stories = instagram_stories_request.json()['data']
                    if len(instagram_stories) > 0:
                        for instagram_story in instagram_stories:
                            # kontrola, jestli náhodou příspěvek již neexistuje
                            post_query = Posts.query.filter_by(platform_id=instagram_post.get("id"), platform_type_id=2)

                            # pokud již existuje, tak pouze aktualizuji data
                            if post_query.one_or_none():
                                post_query.update(
                                    {
                                        "views": instagram_post.get("view_count", None),
                                        "likes": instagram_post.get("like_count", None),
                                        "comments": instagram_post.get("comments_count", None),
                                        "engagement_rate": (
                                            0
                                            if instagram_post.get("view_count", None) == 0
                                            or instagram_post.get("view_count", None) == None
                                            else (
                                                (
                                                    instagram_post.get("like_count", None)
                                                    + instagram_post.get("comments_count", None)
                                                )
                                                / instagram_post.get("view_count", None)
                                                * 100
                                            )
                                        ),
                                    }
                                )
                                continue

                            # IG post = 1, IG story = 2, IG reel = 3, TT video = 4, FB post = _ (nevím)
                            platform_type_id = 1 if instagram_post["media_product_type"] == "FEED" else 3
                            db.session.add(
                                Posts(
                                    platform_id=instagram_post.get("id"),
                                    platform_type_id=platform_type_id,
                                    published_at=parser.parse(instagram_post.get("timestamp", None)),
                                    media_url=instagram_post.get("permalink", None),
                                    thumbnail_url=instagram_post.get("thumbnail_url", None),
                                    views=instagram_post.get("view_count", None),
                                    likes=instagram_post.get("like_count", None),
                                    comments=instagram_post.get("comments_count", None),
                                    engagement_rate=(
                                        0
                                        if instagram_post.get("view_count", None) == 0
                                        or instagram_post.get("view_count", None) == None
                                        else (
                                            (
                                                instagram_post.get("like_count", None)
                                                + instagram_post.get("comments_count", None)
                                            )
                                            / instagram_post.get("view_count", None)
                                            * 100
                                        )
                                    ),
                                    user_id=user.id,
                                    campaign_id=campaign.id,
                                )
                            )
 """

                if campaign.tiktok_video:
                    # získání dat o TT video
                    # https://open.tiktokapis.com/v2/video/list/?fields=id,create_time,video_description,view_count,title
                    # TODO : refresh token může taky vypršet a pak musím někde odvalidovat
                    if user.tiktok_token_expire_at <= datetime.now():
                        tiktok_refresh = post(
                            f"{Config.TIKTOK_API_URL}/oauth/token/",
                            data={
                                "client_key": Config.TIKTOK_CLIENT_KEY,
                                "client_secret": Config.TIKTOK_CLIENT_SECRET,
                                "grant_type": "refresh_token",
                                "refresh_token": user.tiktok_refresh_token,
                            },
                        ).json()
                        user_query.update(
                            {
                                "tiktok_token": tiktok_refresh.get("access_token"),
                                "tiktok_refresh_token": tiktok_refresh.get("refresh_token"),
                                "tiktok_token_expire_at": datetime.now()
                                + timedelta(seconds=tiktok_refresh.get("expires_in")),
                                "tiktok_refresh_token_expire_at": datetime.now()
                                + timedelta(seconds=tiktok_refresh.get("refresh_expires_in")),
                            }
                        )

                    tiktok_videos_request = post(
                        f"{Config.TIKTOK_API_URL}/video/list/?fields=create_time,video_description,view_count,title,comment_count,embed_link,like_count,id,cover_image_url,share_count",
                        headers={"Authorization": f"Bearer {user.tiktok_token}"},
                    )

                    tiktok_videos = tiktok_videos_request.json()["data"]["videos"]
                    if len(tiktok_videos) > 0:
                        for tiktok_video in tiktok_videos:
                            # kontrola, jestli náhodou příspěvek již neexistuje
                            post_query = Posts.query.filter_by(platform_id=tiktok_video.get("id"))

                            # pokud již existuje, tak pouze aktualizuji data
                            if post_query.one_or_none():
                                post_query.update(
                                    {
                                        "views": tiktok_video.get("view_count", None),
                                        "likes": tiktok_video.get("like_count", None),
                                        "comments": tiktok_video.get("comment_count", None),
                                        "shares": tiktok_video.get("share_count", None),
                                        "engagement_rate": (
                                            0
                                            if tiktok_video.get("view_count", None) == 0
                                            or tiktok_video.get("view_count", None) == None
                                            else (
                                                (
                                                    tiktok_video.get("like_count", 0)
                                                    + tiktok_video.get("comment_count", 0)
                                                    + tiktok_video.get("share_count", 0),
                                                )
                                                / tiktok_video.get("view_count", None)
                                                * 100
                                            )
                                        ),
                                    }
                                )
                                continue

                            # IG post = 1, IG story = 2, IG reel = 3, TT video = 4, FB post = _ (nevím)
                            post_hashtags = set(re.findall(r"#(\w+)", tiktok_video.get("video_description")))
                            campaign_hashtags = set(campaign.hashtags.split(","))

                            if post_hashtags == campaign_hashtags:
                                platform_type_id = 4
                                db.session.add(
                                    Posts(
                                        platform_id=tiktok_video.get("id"),
                                        platform_type_id=platform_type_id,
                                        published_at=datetime.fromtimestamp(tiktok_video.get("create_time", None)),
                                        media_url=tiktok_video.get("embed_link", None),
                                        thumbnail_url=tiktok_video.get("cover_image_url", None),
                                        views=tiktok_video.get("view_count", None),
                                        likes=tiktok_video.get("like_count", None),
                                        comments=tiktok_video.get("comment_count", None),
                                        engagement_rate=(
                                            0
                                            if tiktok_video.get("view_count", None) == 0
                                            or tiktok_video.get("view_count", None) == None
                                            else (
                                                (
                                                    tiktok_video.get("like_count", 0)
                                                    + tiktok_video.get("comment_count", 0)
                                                    + tiktok_video.get("share_count", 0),
                                                )
                                                / tiktok_video.get("view_count", None)
                                                * 100
                                            )
                                        ),
                                        user_id=user.id,
                                        campaign_id=campaign.id,
                                    )
                                )

        db.session.commit()


def startup_actions(app_context):
    campaigns = pull_campaings(app_context)
    save_all_users(app_context)
    ids = []
    for campaign in campaigns:
        ids.append(campaign.get("id"))

    campaign_users(app_context, ids)

    get_posts_metrics(app_context)

    # get_profile_metrics(app_context)
