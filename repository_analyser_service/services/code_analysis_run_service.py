from kink import inject, di
from datetime import UTC, datetime

from models.postgres.code_analysis_run import CodeAnalysisRun
from repositories import CodeAnalysisRunRepository


@inject
class CodeAnalysisRunService:

    def update_start_time_of_run(self, run_id: int):
        di[CodeAnalysisRunRepository].update_start_time_of_run(run_id=run_id, start_time=datetime.now(UTC))

    def update_status(self, run_id: int, status: str):
        """Updates the status of a code analysis run."""
        try:
            di[CodeAnalysisRunRepository].update_status(run_id=run_id, status=status)
        except Exception as e:
            raise Exception(f"Failed to update status for run {run_id}: {e}")