from kink import inject
from sqlalchemy.orm import Session

from models.postgres.code_analysis_run import CodeAnalysisRun
from models.postgres.projects import Project
from utils.postgres import get_bind


@inject
class ProjectRepository:

    def __init__(self):
        self._bind = get_bind()

    def insert_project(self, project: Project) -> None:
        with Session(self._bind) as session:
            session.add(project)
            session.commit()

    def get_project_details_by_run(self, run_id: int) -> Project:
        with Session(self._bind) as session:
            return session.query(Project)\
            .join(CodeAnalysisRun, CodeAnalysisRun.project_id == Project.id)\
            .filter(CodeAnalysisRun.id == run_id)\
            .first()


# if __name__ == '__main__':
#     from kink import di
#     res = di[ProjectRepository].get_project_details(1)
#     print(res[0])
