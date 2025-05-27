from kink import inject

from models.neo4j.project_details import ProjectDetails
from schemas.cc_metadata import CodeComprehensionMetadata
from schemas.project import ProjectSchema


@inject()
class NeoModelService:

    def create_project_node(self, project: ProjectSchema, project_metadata: CodeComprehensionMetadata, run_id: int):
        project_details = ProjectDetails(
            name=project.project_name,
            project_id=project.id,
            run_id=run_id,
            organization=project.organization,
            description=project.project_description,
            technology=project_metadata.technology,
            line_of_business=project_metadata.line_of_business,
            sector=project_metadata.sector,
            focus_area=project_metadata.focus_area,
            repo_name=project_metadata.repo_name,
            repo_url=project_metadata.repo_url,
            branch=project_metadata.branch,
            encoding_type=project_metadata.encoding_type,
            actors=project_metadata.actors,
            functional_modules=project_metadata.functional_modules
        )
        project_details.save()
