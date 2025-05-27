from typing import Dict
from pydantic import BaseModel


class ProjectSchema(BaseModel):
    id: int
    project_name: str
    organization: str
    project_description: str
   
    def __init__(self, **data):
        super().__init__(**data)

    def to_Dict(self) -> Dict:
        dict = {
            "id": self.id,
            "project_name": self.project_name,
            "organization": self.organization,
            "project_description": self.project_description
        }
        return dict
