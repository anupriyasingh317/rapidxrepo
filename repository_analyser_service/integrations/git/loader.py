from typing import List, Tuple

from langchain.schema import Document

from integrations.git.repo_loader import GitCodeLoader
from utils.extensions import extensions


class RepoLoader:

    def load_repository(
            self,
            technology: str,
            branch: str,
            repo_url: str
    ) -> Tuple[List[Document], str]:
        if technology.lower() in extensions:
            repository_data, repository_path = GitCodeLoader().loadRepostoryFromGitURL(
                repo_url=repo_url,
                branch=branch,
                filter_extensions=extensions.get(technology.lower())
            )
            return repository_data, repository_path
        raise ValueError(f"`{technology}` language not supported yet.")

    @staticmethod
    def delete_repo(repository_path: str) -> None:
        from shutil import rmtree
        rmtree(repository_path, ignore_errors=True)
