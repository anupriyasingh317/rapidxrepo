import json

from dotenv import load_dotenv

load_dotenv()
import logging.config
import os

from kink import di
from models.postgres.base import Base
from neomodel import db
from services.repo_analyser_service import RepoAnalyserService
from utils.neo4j_driver import neo4j_driver
from utils.postgres import get_bind
from utils.queue_utils import start_consuming
from utils.utils import get_logging_config

Base.metadata.create_all(bind=get_bind())

# Setup logging
config_file_path = get_logging_config()
logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def process_message(message: str, sender_cb):
    print(f"Processing Message {message}")
    message = json.loads(message)
    db.set_connection(driver=neo4j_driver.driver)
    di[RepoAnalyserService].initalize_file_and_prompt_metadata(run_id=message.get("run_id"), sender_cb=sender_cb,
                                                               ingestion_stage_info=message.get("ingestion_stage_info"))


if __name__ == "__main__":
    recv_queue_name = os.environ["REPO_ANALYSER_QUEUE_NAME"]
    start_consuming(recv_queue_name, process_message)
