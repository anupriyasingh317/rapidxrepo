import logging
import os
from datetime import datetime, timezone
from typing import List

from kink import di, inject

from models.postgres.project_prompt_catalog import ProjectPromptCatalog
from repositories.project_prompt_catalog_repository import \
    ProjectPromptCatalogRepository
from repositories.prompt_catalog_repository import PromptCatalogRepository
from services.redis_service import RedisService

UTC = timezone.utc

_LOGGER = logging.getLogger(__name__)
MODEL_PROVIDER = os.environ["MODEL_PROVIDER"]

@inject
class PromptCatalogService:

    def add_prompt_catalog_of_project_into_db(self, project_id: int, tech: str):
        exisiting_prompts_for_project = di[ProjectPromptCatalogRepository].get_exisitng_prompts_of_project(project_id)
        if exisiting_prompts_for_project:
            return exisiting_prompts_for_project

        prompts = di[PromptCatalogRepository].get_prompt_catalog_for_project(MODEL_PROVIDER, tech)

        current_time = datetime.now(UTC)
        project_prompts: List[ProjectPromptCatalog] = []
        for prompt in prompts:
            project_prompt = ProjectPromptCatalog(
                project_id=project_id,
                prompt_catalog_id = prompt.id,
                provider=prompt.provider,
                technology=prompt.technology,
                type=prompt.type,
                attribute=prompt.attribute,
                text=prompt.text,
                created_by="Repo Analyser",
                created_date=current_time,
                updated_by="Repo Analyser",
                updated_date=current_time,
                MatchAttribute=prompt.MatchAttribute,
                MatchAttributeValue=prompt.MatchAttributeValue
            )
            project_prompts.append(project_prompt)
        
        di[ProjectPromptCatalogRepository].insert_project_prompt_catalog(project_prompts)
        return project_prompts


    def load_prompt_catalog_for_project(self, project_id: int, tech: str):
        tech = tech.lower()
        project_prompts = self.add_prompt_catalog_of_project_into_db(project_id, tech)
        di[RedisService].add_prompts_of_project(project_id, project_prompts)

# if __name__ == '__main__':
#     PromptCatalogService().load_prompt_catalog_for_project(1, "c")
