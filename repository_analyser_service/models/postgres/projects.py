from typing import Optional
from uuid import uuid4
from datetime import datetime, UTC
# import sys
# sys.path.append("/workspaces/Hex-ParserRapidx/app-codescout/Parser2.0/repository_analyser_service")
from models.postgres.base import Base
from sqlalchemy import Column, String, ARRAY, INTEGER, TIMESTAMP


class Project(Base):
    __tablename__ = 'projects'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    project_name = Column(String, nullable=False)
    project_description = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    created_date = Column(TIMESTAMP, nullable=False, default=datetime.now(UTC))
    created_by = Column(String, nullable=False)
    updated_date = Column(TIMESTAMP, onupdate=datetime.now(UTC))
    updated_by = Column(String)

