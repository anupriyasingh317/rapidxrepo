from datetime import datetime, UTC
import os
from typing import Optional
from uuid import uuid4

from sqlalchemy import TIMESTAMP, Column, String, INTEGER, ForeignKey, create_engine

from models.postgres.projects import Project
from models.postgres.base import Base


class CodeAnalysisRun(Base):
    __tablename__ = 'code_analysis_run'

    id = Column(INTEGER, autoincrement=True, primary_key=True)
    project_id = Column(INTEGER, ForeignKey(Project.id, ondelete="CASCADE"))
    status = Column(String, default="Initialized")
    analysis_status = Column(String, default="Pending")
    error = Column(String)
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    created_date = Column(TIMESTAMP, nullable=False, default=datetime.now(UTC))
    created_by = Column(String)
    updated_date = Column(TIMESTAMP, onupdate=datetime.now(UTC))
    updated_by = Column(String)

    def __init__(
            self,
            project_id: int,
            start_time: datetime,
            status: Optional[str] = "Initialized",
            error: Optional[str] = None
    ):
        self.project_id = project_id
        self.start_time = start_time
        self.status = status
        self.error = error

        self.created_date = datetime.now(UTC)
        self.created_by = "Repo Analyser"
        self.updated_date = datetime.now(UTC)
        self.updated_by = "Repo Analyser"
        super().__init__()


# DATABASE_URL = os.getenv("POSTGRES_CONN_STR").format(password=os.getenv("POSTGRES_PWD"))
# engine = create_engine(DATABASE_URL, echo=True)

# # Create the new table
# Base.metadata.create_all(engine)