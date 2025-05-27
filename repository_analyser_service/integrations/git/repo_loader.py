import logging.config
import os
from typing import Tuple, List
from uuid import uuid4

from langchain_community.document_loaders import GitLoader
from langchain_core.documents import Document

from utils import utils

config_file_path = utils.get_logging_config()
logging.config.fileConfig(config_file_path, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class GitCodeLoader:

    def get_repo_name_from_url(self, repo_url):
        from urllib.parse import urlparse
        parsed_url = urlparse(repo_url)
        path_parts = parsed_url.path.split('/')
        repo_name_with_ext = path_parts[-1]  # Get the last part which is the repository name with extension (.git)
        repo_name = os.path.splitext(repo_name_with_ext)[0]  # Remove the '.git' extension
        return repo_name

    def loadRepostoryFromGitURL(self, repo_url: str, filter_extensions: list, branch: str) -> Tuple[List[Document], str]:
        repo_name = self.get_repo_name_from_url(repo_url)
        
        temp_dir_path_with_repo_name = os.path.join(os.getenv("CODEBASE_ROOT"), f"{repo_name}_{uuid4()}", repo_name)
        print("created temporary directory", temp_dir_path_with_repo_name)

        loader = GitLoader(
            clone_url=repo_url,
            repo_path=temp_dir_path_with_repo_name,
            branch=branch,
            file_filter=lambda file_path: any(file_path.endswith(ext) for ext in filter_extensions) and (
                    "__init__.py" not in file_path),
        )
        data = loader.load()
        logger.info("*" * 80)

        for d in data:
            logger.info(d.metadata['file_name'])

        return data, temp_dir_path_with_repo_name


if __name__ == '__main__':
    from shutil import rmtree

    data, path = GitCodeLoader().loadRepostoryFromGitURL(
        branch="master",
        repo_url="https://github.com/SiddharthMurjani/snek.git",
        filter_extensions=[".cob", ".cbl"])
    rmtree(path)
    print(len(data))
    print(f"Path {path} deleted")
