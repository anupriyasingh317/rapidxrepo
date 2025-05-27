from kink import inject
from sqlalchemy import update
from sqlalchemy.orm import Session
from datetime import datetime, UTC

from models.postgres.code_analysis_run import CodeAnalysisRun
from utils.postgres import get_bind


@inject
class CodeAnalysisRunRepository:

    def __init__(self):
        self._bind = get_bind()
    
    def update_start_time_of_run(self, run_id, start_time: datetime):
        with Session(self._bind) as session:
            stmt = (
                update(CodeAnalysisRun)
                .where(CodeAnalysisRun.id == run_id)
                .values(start_time=start_time,
                         updated_by = "RepoAnalyserService", 
                         updated_date=datetime.now(UTC))   
            )
            session.execute(stmt)
            session.commit()

    def update_status(self, run_id: int, status: str):
        """Updates the status of the CodeAnalysisRun."""
        with Session(self._bind) as session:
            stmt = (
                update(CodeAnalysisRun)
                .where(CodeAnalysisRun.id == run_id)
                .values(
                    status=status,
                    updated_by="RepoAnalyserService",
                    updated_date=datetime.now(UTC)
                )
            )
            session.execute(stmt)
            session.commit()