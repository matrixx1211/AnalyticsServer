from os import getenv, path

# načti .env ze stejného adresáře
BASE_DIR = path.dirname(__file__)


def env_bool(key: str, default: bool = False) -> bool:
    val = getenv(key, str(int(default)))
    return str(val).lower() in ("1", "true", "yes", "y", "on")


def env_list(key: str, default: list = None) -> list:
    val = getenv(key)
    if val:
        return [item.strip() for item in val.split(",")]
    return default if default is not None else []


class Config:
    # běhové režimy a cesty
    DEV = env_bool("DEV", False)
    DATABASE_PATH = getenv("DATABASE_PATH", "analytics.db")

    # externí API – defaulty, ať to nespadne při importu
    CREATORS_API_URL = getenv("CREATORS_API_URL", "https://creators.contentbox.cz/api").rstrip("/")
    META_API_URL = getenv("META_API_URL", "https://graph.facebook.com/v23.0").rstrip("/")
    TIKTOK_API_URL = getenv("TIKTOK_API_URL", "https://open.tiktokapis.com/v2").rstrip("/")

    TIKTOK_CLIENT_KEY = getenv("TIKTOK_CLIENT_KEY", "sbawm3jxuwfna69ueu")
    TIKTOK_CLIENT_SECRET = getenv("TIKTOK_CLIENT_SECRET", "IiMrQb2YhN3v2Z00Fm6gp2jBqwBWPNl8")

    META_APP_ID = getenv("META_APP_ID", "2037286096678644")
    META_APP_SECRET = getenv("META_APP_SECRET", "8fb3c0270c4513d16ffed2c121098949")

    CORS = env_list("CORS", ["https://creators.contentbox.cz", "https://beautynews.loreal.cz"])

    def __str__(self):
        return f"""
    CONFIGURATION:
            
        - DEV: {self.DEV}

        - DATABASE_PATH: {self.DATABASE_PATH}

        - CREATORS_API_URL: {self.CREATORS_API_URL}
        - META_API_URL: {self.META_API_URL}
        - TIKTOK_API_URL: {self.TIKTOK_API_URL}

        - TIKTOK_CLIENT_KEY: {self.TIKTOK_CLIENT_KEY}
        - TIKTOK_CLIENT_SECRET: {self.TIKTOK_CLIENT_SECRET}
        
        - META_APP_ID: {self.META_APP_ID}
        - META_APP_SECRET: {self.META_APP_SECRET}
        
        - CORS: {self.CORS}
        """

    def __repr__(self):
        return self.__str__()
