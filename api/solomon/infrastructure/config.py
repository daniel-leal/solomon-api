import os

from dotenv import load_dotenv

if os.getenv("DOCKER_ENV"):
    load_dotenv(dotenv_path=".env.docker")
elif os.getenv("ENV") == "test":
    load_dotenv(dotenv_path=".env.test")
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")
EXPIRES_AT = os.getenv("EXPIRES_AT", "")
SECRET_KEY = os.getenv("SECRET_KEY", "")