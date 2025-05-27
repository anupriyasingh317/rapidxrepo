from kink import inject
from sqlalchemy.orm import Session

from models.postgres.code_analysis_run import CodeAnalysisRun
from models.postgres.project_prompt_catalog import ProjectPromptCatalog
from models.postgres.projects import Project
from utils.postgres import get_bind
from datetime import datetime, timezone

UTC = timezone.utc

@inject
class ProjectPromptCatalogRepository:

    def __init__(self):
        self._bind = get_bind()

    def insert_project_prompt_catalog(self, project_prompt_catalogs: list[ProjectPromptCatalog]) -> Project:
        with Session(self._bind, expire_on_commit=False) as session:
            session.add_all(project_prompt_catalogs)
            session.commit()
    
    def get_exisitng_prompts_of_project(self, project_id: int) -> list[ProjectPromptCatalog]:
        with Session(self._bind) as session:
            return session.query(ProjectPromptCatalog)\
                .filter(ProjectPromptCatalog.project_id == project_id)\
                .all()

    def delete_prompts_of_project(self, project_id: int):
        with Session(self._bind) as session:
            session.query(ProjectPromptCatalog) \
            .filter(ProjectPromptCatalog.project_id == project_id) \
            .delete()
            session.commit()
                #.all()




# if __name__ == "__main__":
#     res = ProjectPromptCatalogRepository().get_exisitng_prompts_of_project(33)
#     print(len(res))
#     print(bool(res))