import os
from sqlalchemy import create_engine


def get_bind():
    return create_engine(url=os.environ.get("POSTGRES_URL"), echo=True, connect_args={"prepare_threshold": None})
