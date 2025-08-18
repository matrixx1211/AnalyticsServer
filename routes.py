from flask import Blueprint, jsonify, request
from models import Users, db
from requests import post, get
from dotenv import load_dotenv, dotenv_values

load_dotenv() # Inicializace dot env pro načtení proměnných prostředí
env = dotenv_values(".env")


api = Blueprint('api', __name__, url_prefix='/api')

# ------------------------------------------------------------------------------------------------ #
''' TIKTOK API ENDPOINTS '''
# ------------------------------------------------------------------------------------------------ #

@api.route('/tiktok/token', methods=['POST'])
def get_tiktok_token():
    # získání kódu z požadavku
    body = request.get_json()

    # poslání požadavku na TikTok API pro získání tokenu s pomocí kódu
    tiktok_data = { 'code': body.get('code'),
                   'client_key': env['TIKTOK_CLIENT_KEY'],
                   'client_secret': env['TIKTOK_CLIENT_SECRET'],
                   'grant_type': 'authorization_code',
                   'redirect_uri': body.get('redirect_uri') }
    print(f"Sending data to TikTok API: {tiktok_data}")
    tiktok_headers = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' }
    r = post(env['TIKTOK_API_URL'] + '/oauth/token/',  data=tiktok_data, headers=tiktok_headers, )

    
    # uložení tokenu do databáze
    data = r.json()

    if (data.get('error_description')):
        return jsonify({"error": "expired_code",'original_error': data.get('error'), 'original_error_description': data.get('error_description')}), 400
    
    #Users.query.
    
    return jsonify({'token': data.access_token}), 200

# ------------------------------------------------------------------------------------------------ #
''' FACEBOOK API ENDPOINTS '''
# ------------------------------------------------------------------------------------------------ #

@api.route('/facebook/token', methods=['POST'])
def get_facebook_token():
    # získání tokenu z požadavku
    body = request.get_json()

    # vytvoření uživatele včetně údajů z Facebooku   
    create_user_if_not_exists(email=body.get('email'), meta_token=body.get('token'), meta_expires_at=body.get('expires_in'))

    return jsonify({'token': body.get('token')}), 200


@api.route('/user/<username>', methods=['GET'])
def get_user_data(username):
    """Získání dat uživatele podle uživatelského jména."""
    user = Users.query.filter_by(username=username).first()
    if user:
        return {'id': user.id, 'username': user.username}, 200
    else:
        return {'error': 'User not found'}, 404
    
# ------------------------------------------------------------------------------------------------ #
''' UTILS '''
# ------------------------------------------------------------------------------------------------ #
def create_user_if_not_exists(email, meta_token = None, meta_expires_at = None):
    user = Users.query.filter_by(creators_email=email).first()

    if not user:
        user = Users(creators_email=email)
        db.session.add(user)
        db.session.commit()