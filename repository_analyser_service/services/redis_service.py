import os
from kink import inject
from typing import List
from time import time

from models.postgres.project_prompt_catalog import ProjectPromptCatalog
from utils.redis_driver import redis_connection
import logging

_LOGGER = logging.getLogger(__name__)
PROMPT_CACHE_TTL_IN_SEC = int(os.environ.get("PROMPT_CACHE_TTL_IN_SEC"))

@inject
class RedisService:

    def add_prompts_of_project(self, project_id: int, prompt_catalogs: List[ProjectPromptCatalog]):
        try:
            _LOGGER.info(f"Caching Prompts for the Project {project_id}")
            pipeline = redis_connection.pipeline()
            for prompt_catalog in prompt_catalogs:
                if (prompt_catalog.type == 'service_call' or prompt_catalog.type == 'db_call') and prompt_catalog.attribute == 'business_summary':
                    hash_name = f"{prompt_catalog.type}_{prompt_catalog.attribute}_{prompt_catalog.MatchAttribute}_{project_id}"
                    hash_mapping = {
                        "prompt_id": prompt_catalog.id,
                        "text": prompt_catalog.text,
                        "MatchAttribute": prompt_catalog.MatchAttribute,
                        "MatchAttributeValue": prompt_catalog.MatchAttributeValue
                    }
                else:
                    hash_name = f"{prompt_catalog.type}_{prompt_catalog.attribute}_{project_id}"
                    hash_mapping = {
                        "prompt_id": prompt_catalog.id,
                        "text": prompt_catalog.text
                    }
                pipeline.hset(hash_name.lower(), mapping=hash_mapping)
                pipeline.expire(hash_name, PROMPT_CACHE_TTL_IN_SEC)
            pipeline.execute()
            _LOGGER.info(f"Cached Prompts for the Project {project_id}")
        except Exception as err:
            # Service should not be dependent on redis. so ignoring any errors
            _LOGGER.warning("Error thrown while adding prompts to Cache")
            _LOGGER.warning(err)
