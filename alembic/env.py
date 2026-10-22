import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv


sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))


load_dotenv()


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

from src.database import Base
import src.models  

target_metadata = Base.metadata