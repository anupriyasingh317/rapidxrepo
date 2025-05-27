from datetime import datetime, timezone

from sqlalchemy import (INTEGER, Column, DateTime, ForeignKey, String,
                        UniqueConstraint)
from sqlalchemy.orm import relationship

from models.postgres.base import Base
from models.postgres.projects import Project
from models.postgres.prompt_catalog import PromptCatalog

UTC = timezone.utc

class ProjectPromptCatalog(Base):
    __tablename__ = 'project_prompt_catalog'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    project_id = Column(INTEGER, ForeignKey(Project.id, ondelete="CASCADE"), nullable=False)
    prompt_catalog_id = Column(INTEGER, ForeignKey(PromptCatalog.id, ondelete="CASCADE"), nullable=True)
    parent_project_prompt_id = Column(INTEGER, ForeignKey(id, ondelete="CASCADE"), nullable=True)
    provider = Column(String(20), nullable=False)
    technology = Column(String(20), nullable=False)
    type = Column(String(50), nullable=False)
    attribute = Column(String(50), nullable=False)
    text = Column(String)
    created_by = Column(String(150))
    created_date = Column(DateTime)
    updated_by = Column(String(150))
    updated_date = Column(DateTime)
    MatchAttribute = Column(String(50))
    MatchAttributeValue = Column(String)

    # __table_args__ = (
    #     UniqueConstraint('project_id', 'provider', 'technology', 'type', 'attribute', 'parent_project_prompt_id', name='uq_provider_technology_type_attribute', postgresql_nulls_not_distinct=True),
    # )