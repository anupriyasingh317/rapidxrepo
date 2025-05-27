from typing import Dict, List, Optional
from schemas.project import ProjectSchema
from pydantic import BaseModel, Field


class CodeComprehensionMetadata(BaseModel):
    project_id: int
    technology: str
    repo_name: str = Field(default="NA")
    repo_url: str = Field(default="NA")
    branch: str = Field(default="master")
    # source_type: str = Field(default=CONSTANTS.SOURCE_TYPE.CODE_REPO.value)
    # type_of_data: str = Field(default=CONSTANTS.TYPE_OF_DATA.CODE_SNIPPET.value)
    # In UI make sure to put a small (i) button when hovered tell us the exact meaning of input field,   same as user_declared_root_modules
    root_snippets_dir: Optional[List[str]] = None
    entry_point_dir: str  # same as root
    exclusion_dir: Optional[List[str]] = None
    line_of_business: Optional[str] = None
    sector: Optional[str] = None
    focus_area: Optional[str] = None
    encoding_type: str
    actors: Optional[List[str]] = None

    def __init__(self, **data):
        if data.get("repo_name") is None:
            data["repo_name"] = data.get("project")
        super().__init__(**data)

    # def to_Dict(self) -> Dict:
    #     dict = {}

    #     dict["technology"] = self.technology
    #     dict["repo_url"] = self.repo_url
    #     return dict

    def to_dict(self) -> Dict:
        return {
            "project": self.project.to_dict(),
            "technology": self.technology,
            "repo_name": self.repo_name,
            "repo_url": self.repo_url,
            "branch": self.branch,
            "root_snippets_dir": self.root_snippets_dir,
            "entry_point_dir": self.entry_point_dir,
            "exclusion_dir": self.exclusion_dir,
            "line_of_business": self.line_of_business,
            "sector": self.sector,
            "focus_area": self.focus_area,
            "encoding_type": self.encoding_type,
        }
