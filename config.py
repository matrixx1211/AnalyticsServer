from dotenv import load_dotenv, dotenv_values

load_dotenv()  # Inicializace dot env pro načtení proměnných prostředí
env = dotenv_values(".env")


class Config:
    DEV = env["DEV"]

    DATABASE_PATH = env["DATABASE_PATH"]

    TIKTOK_ORGANIZATION_ID = env["TIKTOK_ORGANIZATION_ID"]
    TIKTOK_CLIENT_KEY = env["TIKTOK_CLIENT_KEY"]
    TIKTOK_CLIENT_SECRET = env["TIKTOK_CLIENT_SECRET"]
    TIKTOK_API_URL = env["TIKTOK_API_URL"]

    META_APP_ID = env["META_APP_ID"]
    META_APP_SECRET = env["META_APP_SECRET"]
    META_API_URL = env["META_API_URL"]

    CREATORS_API_URL = env["CREATORS_API_URL"]
