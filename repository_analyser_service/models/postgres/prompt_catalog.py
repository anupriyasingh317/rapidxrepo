from datetime import timezone, datetime

from sqlalchemy import Column, String, INTEGER, DateTime, UniqueConstraint

from models.postgres.base import Base

UTC = timezone.utc

class PromptCatalog(Base):
    __tablename__ = 'prompt_catalog'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
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

    __table_args__ = (
        UniqueConstraint('provider', 'technology', 'type', 'attribute', name='uq_provider_technology_type_attribute'),
    )