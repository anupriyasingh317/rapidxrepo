import os

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import MetaData

metadata = MetaData(schema=os.environ['POSTGRES_SCHEMA'])


class Base(DeclarativeBase):
    metadata = metadata
