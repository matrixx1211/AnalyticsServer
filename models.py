from flask_sqlalchemy import SQLAlchemy

# Vytvoření instance SQLAlchemy a modelů databáze
db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # data o uživateli, jak jsou v creators appce
    creators_id = db.Column(db.Integer, nullable=True)
    creators_email = db.Column(db.String(250), nullable=False, unique=True)

    # data o facebooku, jako je uživatelské jméno a ID uživatele, které získám při přihlášení (pouze ID)
    facebook_username = db.Column(db.String(50), nullable=True)
    facebook_user_id = db.Column(db.String(50), nullable=True)

    # analytická data z Facebook API
    facebook_total_views = db.Column(db.Integer, nullable=True)
    facebook_total_likes = db.Column(db.Integer, nullable=True)
    facebook_total_comments = db.Column(db.Integer, nullable=True)
    facebook_followers_count = db.Column(db.Integer, nullable=True)
    facebook_profile_picture_url = db.Column(db.Text, nullable=True)
    facebook_avg_views = db.Column(db.Float, nullable=True)
    facebook_avg_likes = db.Column(db.Float, nullable=True)
    facebook_avg_comments = db.Column(db.Float, nullable=True)

    # data o instagramu, jako je uživatelské jméno a ID uživatele, které získám po dvou API voláních (pouze ID)
    instagram_username = db.Column(db.String(50), nullable=True)
    instagram_user_id = db.Column(db.String(50), nullable=True)

    # analytická data z Instagram API
    instagram_total_views = db.Column(db.Integer, nullable=True)
    instagram_total_likes = db.Column(db.Integer, nullable=True)
    instagram_total_comments = db.Column(db.Integer, nullable=True)
    instagram_followers_count = db.Column(db.Integer, nullable=True)
    instagram_profile_picture_url = db.Column(db.Text, nullable=True)
    instagram_avg_views = db.Column(db.Float, nullable=True)
    instagram_avg_likes = db.Column(db.Float, nullable=True)
    instagram_avg_comments = db.Column(db.Float, nullable=True)

    # data o Metě, jako je token a kdy vyprší (platnost by měla být 60 dní nebo 90 dní, ale měla by se obnovovat automaticky)
    meta_token = db.Column(db.Text, nullable=True)
    meta_token_expire_at = db.Column(db.DateTime, nullable=True)
    meta_scopes = db.Column(db.Text, nullable=True)

    # data o TikToku, jako je uživatelské jméno, token a kdy vyprší (platnost by měla být 24 hodin, ale refresh token (slouží k získání nového access tokenu) je platný 365 dní)
    tiktok_username = db.Column(db.String(50), nullable=True)
    tiktok_user_id = db.Column(db.String(50), nullable=True)
    tiktok_token = db.Column(db.Text, nullable=True)
    tiktok_refresh_token = db.Column(db.Text, nullable=True)
    tiktok_token_expire_at = db.Column(db.DateTime, nullable=True)
    tiktok_refresh_token_expire_at = db.Column(db.DateTime, nullable=True)
    tiktok_scopes = db.Column(db.Text, nullable=True)

    # analytická data z TikTok API
    tiktok_total_views = db.Column(db.Integer, nullable=True)
    tiktok_total_likes = db.Column(db.Integer, nullable=True)
    tiktok_total_comments = db.Column(db.Integer, nullable=True)
    tiktok_followers_count = db.Column(db.Integer, nullable=True)
    tiktok_profile_picture_url = db.Column(db.Text, nullable=True)
    tiktok_avg_views = db.Column(db.Float, nullable=True)
    tiktok_avg_likes = db.Column(db.Float, nullable=True)
    tiktok_avg_comments = db.Column(db.Float, nullable=True)

    # data o příspěvcích uživatelů - relace
    posts_data = db.relationship("users_posts_data", back_populates="user", lazy=True)


class UsersPostsData(db.Model):
    __tablename__ = "users_posts_data"

    id = db.Column(db.Integer, primary_key=True)

    # data ohledně toho, odkud je příspěvěk
    platform_id = db.Column(db.Integer, nullable=False)

    # data o příspěvku, jako je název, popisek, datum a URL
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.DateTime, nullable=False)
    hashtags = db.Column(db.String(200), nullable=True)

    media_url = db.Column(db.Text, nullable=False)
    thumbnail_url = db.Column(db.Text, nullable=False)

    # analytická data o příspěvku
    views = db.Column(db.Integer, nullable=False)
    likes = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)

    # data o uživateli, který příspěvek vytvořil - relace
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("users", back_populates="posts_data")
