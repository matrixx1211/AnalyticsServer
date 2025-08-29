from typing import Optional, List
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import String, Text, Boolean, ForeignKey

# Vytvoření instance SQLAlchemy a modelů databáze
db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = "users"

    # Primární klíč pro tabulku uživatelů
    id: Mapped[int] = mapped_column(primary_key=True)

    # data o uživateli, jak jsou v creators appce
    creators_id: Mapped[int]
    creators_email: Mapped[str] = mapped_column(String(250), unique=True)

    # data o facebooku, jako je uživatelské jméno a ID uživatele, které získám při přihlášení (pouze ID)
    facebook_username: Mapped[Optional[str]] = mapped_column(Text)  # již nelze získat
    facebook_user_id: Mapped[Optional[str]] = mapped_column(Text)
    facebook_page_id: Mapped[Optional[str]] = mapped_column(Text)
    facebook_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)

    # data o instagramu, jako je uživatelské jméno a ID uživatele, které získám po dvou API voláních (pouze ID)
    instagram_username: Mapped[Optional[str]] = mapped_column(Text)
    instagram_user_id: Mapped[Optional[str]] = mapped_column(Text)
    instagram_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)

    # data o Metě, jako je token a kdy vyprší (platnost by měla být 60 dní nebo 90 dní, ale měla by se obnovovat automaticky)
    meta_token: Mapped[Optional[str]] = mapped_column(Text)
    meta_token_expire_at: Mapped[Optional[datetime]]
    meta_scopes: Mapped[Optional[str]] = mapped_column(Text)

    # data o TikToku, jako je uživatelské jméno, token a kdy vyprší (platnost by měla být 24 hodin, ale refresh token (slouží k získání nového access tokenu) je platný 365 dní)
    tiktok_username: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_user_id: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_token: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_token_expire_at: Mapped[Optional[datetime]]
    tiktok_refresh_token_expire_at: Mapped[Optional[datetime]]
    tiktok_scopes: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)

    # relace s jinými tabulkami (připojuje se k posts_data a analytics_data)
    posts_data: Mapped[Optional[List["Posts"]]] = relationship(back_populates="user", lazy=True)
    analytics_data: Mapped[Optional[List["AnalyticsData"]]] = relationship(back_populates="user", lazy=True)

    def to_dict(self):
        return {"creators_id": self.creators_id, "creators_email": self.creators_email}

    def dev_to_dict(self):
        return {
            "creators_id": self.creators_id,
            "creators_email": self.creators_email,
            "facebook_username": self.facebook_username,
            "facebook_user_id": self.facebook_user_id,
            "facebook_page_id": self.facebook_page_id,
            "facebook_profile_picture_url": self.facebook_profile_picture_url,
            "instagram_username": self.instagram_username,
            "instagram_user_id": self.instagram_user_id,
            "instagram_profile_picture_url": self.instagram_profile_picture_url,
            "meta_token": self.meta_token,
            "meta_token_expire_at": self.meta_token_expire_at,
            "meta_scopes": self.meta_scopes,
            "tiktok_username": self.tiktok_username,
            "tiktok_user_id": self.tiktok_user_id,
            "tiktok_profile_picture_url": self.tiktok_profile_picture_url,
            "tiktok_token": self.tiktok_token,
            "tiktok_refresh_token": self.tiktok_refresh_token,
            "tiktok_token_expire_at": self.tiktok_token_expire_at,
            "tiktok_refresh_token_expire_at": self.tiktok_refresh_token_expire_at,
            "tiktok_scopes": self.tiktok_scopes,
        }


class Posts(db.Model):
    __tablename__ = "posts"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # ID příspěvku na dané platformě
    platform_id: Mapped[str] = mapped_column(String(100))

    # data ohledně toho, odkud je příspěvek
    platform_type_id: Mapped[int]
    # TODO: možná by nebylo od věci zde přidat typ, ale asi bude stačit platform_type_id

    # data o příspěvku, jako je název, popisek, datum a URL
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[datetime]
    hashtags: Mapped[Optional[str]] = mapped_column(Text)

    media_url: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)

    media_type: Mapped[Optional[str]] = mapped_column(String(8))

    # analytická data o příspěvku
    views: Mapped[Optional[int]]
    likes: Mapped[Optional[int]]
    shares: Mapped[Optional[int]]
    comments: Mapped[Optional[int]]

    engagement_rate: Mapped[Optional[float]]  # TODO: výpočet z likes + comments + shares / views * 100 [%]

    # data o uživateli, který příspěvek vytvořil - relace
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Users] = relationship(back_populates="posts_data")

    # data o kampani, ke které příspěvek patří - relace
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    campaign: Mapped["Campaigns"] = relationship(back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            # "platform_id": self.platform_id,
            "platform_type_id": self.platform_type_id,
            # "title": self.title,
            # "description": self.description,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            # "hashtags": self.hashtags,
            "media_url": self.media_url,
            "thumbnail_url": self.thumbnail_url,
            "media_type": self.media_type,
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "engagement_rate": self.engagement_rate,
            # "user_id": self.user_id,
            # "campaign_id": self.campaign_id,
            "user": self.user.to_dict() if self.user else None,
        }

    def dev_to_dict(self):
        return {
            "platform_id": self.platform_id,
            "platform_type_id": self.platform_type_id,
            "title": self.title,
            "description": self.description,
            "published_at": self.published_at,
            "hashtags": self.hashtags,
            "media_url": self.media_url,
            "thumbnail_url": self.thumbnail_url,
            "media_type": self.media_type,
            "views": self.views,
            "likes": self.likes,
            "shares": self.shares,
            "comments": self.comments,
            "engagement_rate": self.engagement_rate,
            "user_id": self.user_id,
            "user": self.user.to_dict() if self.user else None,
            "campaign_id": self.campaign_id,
        }


class Campaigns(db.Model):
    __tablename__ = "campaigns"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # ID kampaně z Creators aplikace
    creators_id: Mapped[int]

    # Jméno kampaně a hashtagy, které se budou hledat
    name: Mapped[str] = mapped_column(String(100))
    hashtags: Mapped[str] = mapped_column(Text)

    # Typ obsahu, pro který je kampaň určená (výchozí hodnota je False)
    instagram_reel: Mapped[bool] = mapped_column(Boolean, default=False)
    instagram_post: Mapped[bool] = mapped_column(Boolean, default=False)
    instagram_story: Mapped[bool] = mapped_column(Boolean, default=False)
    tiktok_video: Mapped[bool] = mapped_column(Boolean, default=False)
    facebook_post: Mapped[bool] = mapped_column(Boolean, default=False)

    # Časové omezení kampaně, kdy se budou získávat data o nich
    start_date: Mapped[Optional[date]]
    end_date: Mapped[Optional[date]]
    ended: Mapped[bool] = mapped_column(Boolean, default=False)

    posts: Mapped[Optional[List[Posts]]] = relationship(back_populates="campaign")

    def dev_to_dict(self):
        return {
            "creators_id": self.creators_id,
            "name": self.name,
            "hashtags": self.hashtags,
            "instagram_reel": self.instagram_reel,
            "instagram_post": self.instagram_post,
            "instagram_story": self.instagram_story,
            "tiktok_video": self.tiktok_video,
            "facebook_post": self.facebook_post,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "ended": self.ended,
        }


class AnalyticsData(db.Model):
    __tablename__ = "analytics_data"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # Měsíc pro který analytická data jsou
    month: Mapped[int]

    # analytická data z Facebook API
    facebook_total_views: Mapped[Optional[int]]
    facebook_total_likes: Mapped[Optional[int]]
    facebook_total_comments: Mapped[Optional[int]]
    facebook_followers_count: Mapped[Optional[int]]
    facebook_avg_views: Mapped[Optional[float]]
    facebook_avg_likes: Mapped[Optional[float]]
    facebook_avg_comments: Mapped[Optional[float]]
    facebook_engagement_rate: Mapped[
        Optional[float]
    ]  # TODO: výpočet likes + comments + shares + (?saves?) / followers * 100 [%]

    # analytická data z Instagram API
    instagram_total_views: Mapped[Optional[int]]
    instagram_total_likes: Mapped[Optional[int]]
    instagram_total_comments: Mapped[Optional[int]]
    instagram_followers_count: Mapped[Optional[int]]
    instagram_avg_views: Mapped[Optional[float]]
    instagram_avg_likes: Mapped[Optional[float]]
    instagram_avg_comments: Mapped[Optional[float]]
    instagram_engagement_rate: Mapped[
        Optional[float]
    ]  # TODO: výpočet likes + comments + shares + (? ?) / followers * 100 [%]

    # analytická data z TikTok API
    tiktok_total_views: Mapped[Optional[int]]
    tiktok_total_likes: Mapped[Optional[int]]
    tiktok_total_comments: Mapped[Optional[int]]
    tiktok_followers_count: Mapped[Optional[int]]
    tiktok_avg_views: Mapped[Optional[float]]
    tiktok_avg_likes: Mapped[Optional[float]]
    tiktok_avg_comments: Mapped[Optional[float]]
    tiktok_engagement_rate: Mapped[
        Optional[float]
    ]  # TODO: výpočet likes + comments + shares + (?saves?) / followers * 100 [%]

    # Relace s uživatelem
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Users] = relationship(back_populates="analytics_data")

    def to_dict(self):
        return {
            "facebook_total_views": self.facebook_total_views,
            "facebook_total_likes": self.facebook_total_likes,
            "facebook_total_comments": self.facebook_total_comments,
            "facebook_followers_count": self.facebook_followers_count,
            "facebook_avg_views": self.facebook_avg_views,
            "facebook_avg_likes": self.facebook_avg_likes,
            "facebook_avg_comments": self.facebook_avg_comments,
            "facebook_engagement_rate": self.facebook_engagement_rate,
            "instagram_total_views": self.instagram_total_views,
            "instagram_total_likes": self.instagram_total_likes,
            "instagram_total_comments": self.instagram_total_comments,
            "instagram_followers_count": self.instagram_followers_count,
            "instagram_avg_views": self.instagram_avg_views,
            "instagram_avg_likes": self.instagram_avg_likes,
            "instagram_avg_comments": self.instagram_avg_comments,
            "instagram_engagement_rate": self.instagram_engagement_rate,
            "tiktok_total_views": self.tiktok_total_views,
            "tiktok_total_likes": self.tiktok_total_likes,
            "tiktok_total_comments": self.tiktok_total_comments,
            "tiktok_followers_count": self.tiktok_followers_count,
            "tiktok_avg_views": self.tiktok_avg_views,
            "tiktok_avg_likes": self.tiktok_avg_likes,
            "tiktok_avg_comments": self.tiktok_avg_comments,
            "tiktok_engagement_rate": self.tiktok_engagement_rate,
            "user_id": self.user_id,
            "user": self.user.to_dict() if self.user else None,
        }


class CampaignUsers(db.Model):
    __tablename__ = "campaign_users"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # Cizí klíče
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
