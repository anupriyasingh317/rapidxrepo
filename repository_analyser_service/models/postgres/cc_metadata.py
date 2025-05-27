import os
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from models.postgres.base import Base
from models.postgres.projects import Project
from sqlalchemy import (ARRAY, INTEGER, TIMESTAMP, CheckConstraint, Column, ForeignKey, String,
                        create_engine)
from sqlalchemy.dialects.postgresql import JSONB


class CodeComprehensionMetaData(Base):
    __tablename__ = 'code_comprehension_metadata'

    # id = Column(INTEGER, autoincrement=True, primary_key=True)
    project_id = Column(INTEGER, ForeignKey(Project.id, ondelete="CASCADE"), primary_key=True)
    technology = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    repo_url = Column(String, nullable=False)
    repo_location = Column(String(5), CheckConstraint("repo_location in ('git', 'local')"), default="git")
    repo_path = Column(String, nullable=True)
    branch = Column(String, default="main")
    line_of_business = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    focus_area = Column(String, nullable=False)
    encoding_type = Column(String, nullable=False)
    root_snippets_directory = Column(ARRAY(String))
    entry_point_directory = Column(String, nullable=False)
    exclude_directory = Column(ARRAY(String))
    actors = Column(ARRAY(String))
    created_date = Column(TIMESTAMP, nullable=False, default=datetime.now(UTC))
    created_by = Column(String, nullable=False)
    updated_date = Column(TIMESTAMP, onupdate=datetime.now(UTC))
    updated_by = Column(String)
    functional_modules = Column(JSONB, nullable=True)
    ingestion_stage = Column(JSONB, nullable=True)


# load_dotenv()
# engine = create_engine(os.getenv("POSTGRES_CONN_STR").format(password=os.getenv("POSTGRES_PWD")), echo=True)

# Base.metadata.drop_all(engine, cascade=True)

# Recreate all tables in the schema
# Base.metadata.create_all(engine)
