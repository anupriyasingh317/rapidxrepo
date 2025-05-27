from typing import List

from kink import inject
from sqlalchemy.orm import Session
from utils.postgres import get_bind

from models.postgres.code_analysis_run_file import CodeAnalysisRunFile


@inject
class CodeAnalysisRunFileRepository:

    def __init__(self):
        self._bind = get_bind()

    def insert_code_analysis_run_file(self, run_files: List[CodeAnalysisRunFile]):
        with Session(self._bind, expire_on_commit=False) as session:
            # session.add(code_analysis_run_file)
            session.bulk_save_objects(run_files, return_defaults=True)
            session.commit()
        return [run_file.id for run_file in run_files]
