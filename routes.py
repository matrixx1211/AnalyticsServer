from flask import Blueprint, jsonify, request, current_app
from requests import post, get

from models import Users, Posts, Campaigns, AnalyticsData
from config import Config

from datetime import datetime, timedelta
from utils import update_user, save_all_users, get_posts_metrics


api = Blueprint("api", __name__, url_prefix="/api")

# ------------------------------------------------------------------------------------------------ #
""" TIKTOK API ENDPOINTS """
# ------------------------------------------------------------------------------------------------ #


@api.route("/tiktok/token", methods=["POST"])
def get_tiktok_token():
    # získání kódu z požadavku
    body = request.get_json()

    # TODO: zde přidat kontrolu, že uživatel je již v DB, protože momentálně nemusím mít creators_id a to by mohl být problém, ale můžu to zároveň vyřešit při 24 jobu, kde prostě se podívám, jestli nějaký acc nemá creators_id
    # předtím, než vůbec začnu řešit uživatele, tak si uložím všechny existující
    # save_all_users(current_app.app_context())

    # poslání požadavku na TikTok API pro získání tokenu s pomocí kódu
    try:
        token_request = post(
            Config.TIKTOK_API_URL + "/oauth/token/",
            data={
                "code": body.get("code"),
                "client_key": Config.TIKTOK_CLIENT_KEY,
                "client_secret": Config.TIKTOK_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": body.get("redirect_uri"),
            },
        )
    except:
        return (
            jsonify(
                {
                    "error": "tiktok_token_request_failed",
                    "error_description": "Request for tiktok access_token failed.",
                }
            ),
            400,
        )

    # uložení tokenu do databáze
    token = token_request.json()

    if token.get("error_description"):
        return (
            jsonify(
                {
                    "error": "expired_code",
                    "original_error": token.get("error"),
                    "original_error_description": token.get("error_description"),
                }
            ),
            400,
        )

    update_user(
        {
            "creators_email": body["email"],
            "tiktok_username": None,
            "tiktok_user_id": token["open_id"],
            "tiktok_token": token["access_token"],
            "tiktok_refresh_token": token["refresh_token"],
            "tiktok_token_expire_at": datetime.now() + timedelta(seconds=token["expires_in"]),
            "tiktok_refresh_token_expire_at": datetime.now() + timedelta(seconds=token["refresh_expires_in"]),
            "tiktok_scopes": body["tiktok_scopes"],
        }
    )

    return jsonify({"token": token["access_token"]}), 200


# ------------------------------------------------------------------------------------------------ #
""" FACEBOOK API ENDPOINTS """
# ------------------------------------------------------------------------------------------------ #


@api.route("/facebook/token", methods=["POST"])
def get_facebook_token():
    # získání short lived tokenu z požadavku
    body = request.get_json()

    # získání long lived tokenu z FB
    try:
        long_lived_token_request = get(
            f"{Config.META_API_URL}/oauth/access_token?grant_type=fb_exchange_token&client_id={Config.META_APP_ID}&client_secret={Config.META_APP_SECRET}&fb_exchange_token={body.get('meta_token')}"
        ).json()

        long_lived_token = long_lived_token_request.get("access_token", None)
        long_lived_token_expires_in = long_lived_token_request.get("expires_in", 5184000)
    except:
        return (
            jsonify(
                {
                    "error": "long_lived_token_retriev_failed",
                    "error_description": "Failed to retrive long lived token from short lived token.",
                }
            )
        ), 400

    # najití ostatních META (FB/IG) údajů a jejich příprava uložení
    # /facebook_user_id/accounts/?access_token=meta_token
    try:
        page_id_request = get(
            f"{Config.META_API_URL}/{body.get('facebook_user_id')}/accounts/?access_token={long_lived_token}"
        )
        data_page_id = page_id_request.json()
    except:
        return (
            jsonify(
                {
                    "error": "page_id_request_failed",
                    "error_description": "Request for page_id failed.",
                }
            ),
            400,
        )

    # FIXME: zde získávám page_id, kde podle všeho může být víc, jak jedna, protože vrací pole, takže možný budoucí problém
    # /page_id[0].id?fields=instagram_business_account&access_token=meta_token
    try:
        ig_user_id_request = get(
            f"{Config.META_API_URL}/{data_page_id['data'][0]['id']}/?fields=instagram_business_account,username&access_token={long_lived_token}"
        )
        ig_user_id_data = ig_user_id_request.json()
    except:
        return (
            jsonify(
                {
                    "error": "page_id_doesnt_exist",
                    "error_description": "This facebook account probably doesn't have page_id.",
                }
            ),
            400,
        )

    # Aktualizace uživatele včetně údajů z Facebooku
    if not update_user(
        {
            "creators_email": body.get("email"),
            "meta_token": long_lived_token,
            "meta_token_expire_at": datetime.now() + timedelta(seconds=long_lived_token_expires_in),
            "meta_scopes": body.get("meta_scopes"),
            "facebook_user_id": body.get("facebook_user_id"),
            "facebook_page_id": data_page_id["data"][0]["id"],
            "instagram_username": ig_user_id_data["username"],
            "instagram_user_id": ig_user_id_data["instagram_business_account"]["id"],
        }
    ):
        return (
            jsonify(
                {
                    "error": "user_not_exist",
                    "error_description": f"The user with this email address {body.get('email')} does not exist.",
                }
            ),
            400,
        )

    return jsonify({"token": body.get("meta_token")}), 200


# ------------------------------------------------------------------------------------------------ #
""" OWN API - RESPONSE FOR CREATORS APP  """
# ------------------------------------------------------------------------------------------------ #


@api.route("/user/valid", methods=["GET"])
def get_is_user_valid():
    creators_id = request.args.get("id")
    creators_email = request.args.get("email")

    if not creators_id or not creators_email:
        return (
            jsonify(
                {
                    "error": "id_or_email_not_entered",
                    "error_description": f"Some required query params not entered, require email {creators_email} and id {creators_id}. Both are required because of how is ",
                }
            ),
            400,
        )

    user_query = Users.query.filter_by(creators_id=creators_id, creators_email=creators_email)
    user = user_query.first()

    if not user:
        return jsonify({"error": "user_not_found", "error_description": f"This user doesn't exist."}), 404

    return jsonify(
        {
            "data": {
                "tiktok_valid": (
                    user.tiktok_refresh_token_expire_at > datetime.now()
                    if user.tiktok_refresh_token_expire_at is not None
                    else False
                ),
                "meta_valid": (
                    user.meta_token_expire_at > datetime.now() if user.meta_token_expire_at is not None else False
                ),
            }
        }
    )


@api.route("/metrics/post", methods=["GET"])
def get_post_metrics():
    # získání ID kampaně
    creators_campaign_id = request.args.get("campaign_id", type=int)

    # oveření zda ID kampaně bylo zadáno
    if creators_campaign_id == None:
        return (
            jsonify(
                {
                    "error": "campaign_id_not_entered",
                    "error_description": "Required query parameter campaign_id not entered.",
                }
            ),
            400,
        )

    # kontrola zda vůbec taková kampaň existuje
    campaign = Campaigns.query.filter_by(creators_id=creators_campaign_id).first()
    if campaign == None:
        return (
            jsonify(
                {
                    "error": "no_campaign_with_campaign_id",
                    "error_description": f"There is no campaign with campaign_id {creators_campaign_id}.",
                }
            ),
            404,
        )

    # získání lokální ID kampaně
    campaign_id = campaign.id

    # pokud je ID kampaně, tak vyhledám informace o kampani a vrátím je
    posts_query = Posts.query.filter_by(campaign_id=campaign_id)

    posts = posts_query.all()

    return jsonify({"creators_campaign_id": creators_campaign_id, "posts": [post.to_dict() for post in posts]}), 200


@api.route("/metrics/profile", methods=["GET"])
def get_profile_metrics():
    # jeden z nich pouze stačí, ideálně oba pro bezpečnost
    user_id = request.args.get("id")

    if user_id is None:
        return (
            jsonify(
                {
                    "error": "user_id_not_entered",
                    "error_description": "No user_id entered. You need to enter valid user_id.",
                }
            ),
            400,
        )

    user = Users.query.filter_by(creators_id=user_id).first()

    if user is None:
        return (
            jsonify(
                {
                    "error": "user_with_user_id_doesnt_exist",
                    "error_description": f"User with user_id {user_id} does not exist.",
                }
            ),
            400,
        )

    analytics_data = AnalyticsData.query.filter_by(user_id=user.id, month=datetime.now().month).first()

    # TODO: místo else {} možná by nebylo od věci raději zavolat funkci, které se pokusí ty data získat
    return jsonify({"data": {"analytics": analytics_data.to_dict() if analytics_data is not None else {}}}), 200


@api.route("/metrics/posts/refresh/all", methods=["GET"])
def force_update_posts_metrics():
    start = datetime.now()
    get_posts_metrics(current_app.app_context())
    end = datetime.now()

    return jsonify({"refresh": {"started_at": start, "ended_at": end}}), 200


# TODO: zde ještě 1x /metrics/posts/refresh?user_id ...


# ------------------------------------------------------------------------------------------------ #
""" DEV ONLY API """
# ------------------------------------------------------------------------------------------------ #
dev = Blueprint("dev", __name__, url_prefix="/dev")


@dev.route("/users", methods=["GET"])
def get_all_users_in_db():
    password = request.args.get("password")
    if password is None:
        return jsonify({"error": "password_not_entered"})

    if password != "t3st@s3rvEr!":
        return jsonify({"error": "no_match_for_password"})

    all_users = Users.query.all()

    return jsonify({"data": {"users": [user.dev_to_dict() for user in all_users]}}), 200


@dev.route("/posts", methods=["GET"])
def get_all_posts_in_db():
    password = request.args.get("password")
    if password is None:
        return jsonify({"error": "password_not_entered"})

    if password != "t3st@s3rvEr!":
        return jsonify({"error": "no_match_for_password"})

    all_posts = Posts.query.all()

    return jsonify({"data": {"posts": [post.dev_to_dict() for post in all_posts]}}), 200


@dev.route("/campaigns", methods=["GET"])
def get_all_campaigns_in_db():
    password = request.args.get("password")
    if password is None:
        return jsonify({"error": "password_not_entered"})

    if password != "t3st@s3rvEr!":
        return jsonify({"error": "no_match_for_password"})

    all_campaigns = Campaigns.query.all()

    return jsonify({"data": {"campaigns": [campaign.dev_to_dict() for campaign in all_campaigns]}}), 200


@dev.route("/now", methods=["GET"])
def get_now():
    return jsonify({"now": datetime.now()}), 200
