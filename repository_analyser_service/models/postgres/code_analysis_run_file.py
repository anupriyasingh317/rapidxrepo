import os
from typing import Optional
from datetime import datetime, UTC

from sqlalchemy import TIMESTAMP, Column, String, INTEGER, ForeignKey, create_engine

from models.postgres.code_analysis_run import CodeAnalysisRun
from models.postgres.base import Base
from sqlalchemy.dialects.postgresql import JSONB


class CodeAnalysisRunFile(Base):
    __tablename__ = 'code_analysis_run_file'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    code_analysis_run_id = Column(INTEGER, ForeignKey(CodeAnalysisRun.id, ondelete="CASCADE"))
    file_path = Column(String, nullable=False)
    parse_status = Column(String)
    snippet_analysis_status = Column(String)
    file_metadata = Column(JSONB, nullable=True)
    created_date = Column(TIMESTAMP, nullable=False, default=datetime.now(UTC))
    created_by = Column(String, nullable=False)
    updated_date = Column(TIMESTAMP, onupdate=datetime.now(UTC))
    updated_by = Column(String)

    def __init__(
            self,
            code_analysis_run_id: int,
            file_path: str,
            file_metadata: dict,
            parse_status: Optional[str] = "Pending",
            snippet_analysis_status: Optional[str] = "Pending"
    ):
        self.code_analysis_run_id = code_analysis_run_id
        self.file_path = file_path
        self.parse_status = parse_status
        self.snippet_analysis_status = snippet_analysis_status
        self.file_metadata = file_metadata

        # self.created_date = datetime.now(UTC)
        self.created_by = "Repo Analyser"
        self.updated_date = datetime.now(UTC)
        self.updated_by = "Repo Analyser"
        super().__init__()


# engine = create_engine(os.getenv("POSTGRES_CONN_STR").format(password=os.getenv("POSTGRES_PWD")), echo=True)
# Base.metadata.drop_all(engine)
# # Create the new table
# Base.metadata.create_all(engine)
