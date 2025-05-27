from kink import inject
from sqlalchemy.orm import Session

from models.postgres.cc_metadata import CodeComprehensionMetaData
from utils.postgres import get_bind


@inject
class CodeComprehensionMetaDataRepository:

    def __init__(self):
        self._bind = get_bind()

    def get_metadata_details(self, project_id: int):
        with Session(self._bind) as session:
            return session.query(CodeComprehensionMetaData)\
                .filter(CodeComprehensionMetaData.project_id == project_id)\
                .first()

