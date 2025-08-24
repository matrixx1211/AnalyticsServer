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

    # data o instagramu, jako je uživatelské jméno a ID uživatele, které získám po dvou API voláních (pouze ID)
    instagram_username: Mapped[Optional[str]] = mapped_column(Text)
    instagram_user_id: Mapped[Optional[str]] = mapped_column(Text)

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

    # relace s jinými tabulkami (připojuje se k posts_data a analytics_data)
    posts_data: Mapped[Optional[List["Posts"]]] = relationship(back_populates="user", lazy=True)
    analytics_data: Mapped[Optional[List["AnalyticsData"]]] = relationship(back_populates="user", lazy=True)


class Posts(db.Model):
    __tablename__ = "posts"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # data ohledně toho, odkud je příspěvek
    platform_id: Mapped[int]

    # data o příspěvku, jako je název, popisek, datum a URL
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime]
    hashtags: Mapped[Optional[str]] = mapped_column(Text)

    media_url: Mapped[str] = mapped_column(Text)
    thumbnail_url: Mapped[str] = mapped_column(Text)

    # analytická data o příspěvku
    views: Mapped[int]
    likes: Mapped[int]
    comments: Mapped[int]

    engagement_rate: Mapped[float]  # TODO: výpočet z likes + comments + shares / views * 100 [%]

    # data o uživateli, který příspěvek vytvořil - relace
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Users] = relationship(back_populates="posts_data")

    # data o kampani, ke které příspěvek patří - relace
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    campaign: Mapped["Campaigns"] = relationship(back_populates="posts")


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
    facebook_posts: Mapped[bool] = mapped_column(Boolean, default=False)

    # Časové omezení kampaně, kdy se budou získávat data o nich
    start_date: Mapped[Optional[date]]
    end_date: Mapped[Optional[date]]
    ended: Mapped[bool] = mapped_column(Boolean, default=False)

    posts: Mapped[Optional[List[Posts]]] = relationship(back_populates="campaign")


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
    facebook_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)
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
    instagram_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)
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
    tiktok_profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)
    tiktok_avg_views: Mapped[Optional[float]]
    tiktok_avg_likes: Mapped[Optional[float]]
    tiktok_avg_comments: Mapped[Optional[float]]
    tiktok_engagement_rate: Mapped[
        Optional[float]
    ]  # TODO: výpočet likes + comments + shares + (?saves?) / followers * 100 [%]

    # Relace s uživatelem
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Users] = relationship(back_populates="analytics_data")


class CampaignUsers(db.Model):
    __tablename__ = "campaign_users"

    # Primární klíč tabulky
    id: Mapped[int] = mapped_column(primary_key=True)

    # Cizí klíče
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
