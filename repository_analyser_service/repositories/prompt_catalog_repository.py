from kink import inject
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy import select

from models.postgres.code_analysis_run import CodeAnalysisRun
from models.postgres.prompt_catalog import PromptCatalog
from utils.postgres import get_bind
from models.postgres.projects import Project

@inject
class PromptCatalogRepository:

    def __init__(self):
        self._bind = get_bind()

    def get_prompt_catalog_for_project(self, model_provider: str, tech: str) -> list[PromptCatalog]:
        with Session(self._bind) as session:
            return session.query(PromptCatalog)\
                .where(PromptCatalog.technology.in_((tech, "all"))) \
                .where(PromptCatalog.provider.in_((model_provider, "all")))\
                .order_by(PromptCatalog.id)\
                .all()

    def get_all_prompt_catalog(self):
        with Session(self._bind) as session:
            return session.query(PromptCatalog) \
                .order_by(PromptCatalog.id) \
                .all()

    def get_all_prompt_for_tech(self, tech: str) -> list[PromptCatalog]:
        with Session(self._bind) as session:
            return (
                session.query(PromptCatalog)
                .where(PromptCatalog.technology.in_((tech, "all")))
                .order_by(PromptCatalog.id)
                .all()
            )


    def truncate_prompt_catalog(self):
        with Session(self._bind) as session:
            #return (
            session.execute(text("Truncate table codebits.prompt_catalog CASCADE"))
            session.commit()
            #)

    def insert_prompt_catalog(self, prompt_catalogs: list[PromptCatalog]) -> Project:
        with Session(self._bind, expire_on_commit=False) as session:
            session.add_all(prompt_catalogs)
            session.commit()

