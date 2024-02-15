import os

from dotenv import load_dotenv

if os.getenv("DOCKER_ENV"):
    load_dotenv(dotenv_path=".env.docker")
elif os.getenv("ENV") == "test":
    load_dotenv(dotenv_path=".env.test")
else:
    load_dotenv(dotenv_path=".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")
EXPIRES_AT = int(os.getenv("EXPIRES_AT", "84600"))
SECRET_KEY = os.getenv("SECRET_KEY", "")
