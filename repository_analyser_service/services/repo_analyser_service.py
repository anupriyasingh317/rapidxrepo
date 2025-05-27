import os
from datetime import datetime, UTC
from pathlib import Path
from kink import inject, di
from services.event_log_service import log_error_event, log_event
from services.neomodel_service import NeoModelService
from services.prompt_catalog_service import PromptCatalogService
from integrations.git import RepoLoader
from models.postgres.code_analysis_run_file import CodeAnalysisRunFile
from repositories import ProjectRepository, CodeAnalysisRunFileRepository, CodeComprehensionMetaDataRepository
from utils.extensions import extensions
from services.code_analysis_run_service import CodeAnalysisRunService
from enums.ingestion_stage import IngestionStage
from models.neo4j.project_details import ProjectDetails, UserVerifiedGroups
from models.postgres.projects import Project
from models.postgres.cc_metadata import CodeComprehensionMetaData
import json
from services.cobol_merger import CobolMerger


@inject
class RepoAnalyserService:

    def initalize_file_and_prompt_metadata(self, run_id: int, sender_cb, ingestion_stage_info: dict):
        start_date = datetime.now(UTC).isoformat()
        di[CodeAnalysisRunService].update_start_time_of_run(run_id=run_id)
        try:
            project = di[ProjectRepository].get_project_details_by_run(run_id=run_id)
            project_data = di[CodeComprehensionMetaDataRepository].get_metadata_details(project_id=project.id)

            di[PromptCatalogService].load_prompt_catalog_for_project(project.id, project_data.technology)
            self.discover_files(run_id, project, project_data, sender_cb, ingestion_stage_info)

            end_date = datetime.now(UTC).isoformat()
            log_event(sender_cb, run_id, run_id, "run", "Repo Analyzer",
                      "Repository cloned and files discovered.", start_date, end_date)
        except Exception as err:
            log_error_event(sender_cb, run_id, run_id, "run", "Repo Analyzer", "Repo Analyzer", err, start_date)
            raise
    
    def get_metadata_of_files(self, repo_path: str):
        metadata_path = Path(f"{repo_path}/repo-metadata.txt")
        if not metadata_path.exists():
            return dict()
        
        repo_metadata = dict()
        raw_metadata = metadata_path.read_text()
        for metadata in raw_metadata.splitlines():
            file, file_metadata = metadata.split("=")
            full_file_path = Path(f"{repo_path}").joinpath(file)
            repo_metadata[full_file_path.as_posix()] = json.loads(file_metadata)
        return repo_metadata


    def discover_files(self, run_id: int, project: Project, project_data: CodeComprehensionMetaData, sender_cb, ingestion_stage_info: dict):

        path = ""
        if project_data.repo_location == "local":
            path = project_data.repo_path
        else:
            data, path = self.__clone_repo(
                branch=project_data.branch,
                repo_url=project_data.repo_url,
                technology=project_data.technology,
                run_id=run_id
            )

        di[CodeAnalysisRunService].update_status(run_id, "Cloning Completed")
        repo_metadata = self.get_metadata_of_files(path)
        # If exclude_directories is empty, include all directories
        if project_data.exclude_directory == [""]:
            def exclude_check(dir_name, d):
                return False
        else:
            def exclude_check(dir_name, d):
                # Construct full path for current item
                full_path = os.path.join(dir_name, d)
                # Normalize paths to ensure proper comparison
                normalized_full_path = os.path.normpath(full_path)
                # Check if any part of the full path matches any exclusion entry
                return any(
                    normalized_full_path.endswith(os.path.normpath(ex_dir))
                    for ex_dir in project_data.exclude_directory)

        run_files = []
        cobol_merger = CobolMerger()
        run_files_dict = dict()
        for dname, dirs, files in os.walk(path):
            di[CodeAnalysisRunService].update_status(run_id, "File discovery Inprogress")
            # Check if any excluded directory is a subdirectory of the current directory
            dirs[:] = [d for d in dirs if not exclude_check(dname, d) and not d.startswith(".")]
            for file_name in files:
                if any(file_name.lower().endswith(ext.lower()) for ext in
                        extensions.get(project_data.technology.lower())) or "." not in file_name:

                    file_path = os.path.join(dname, file_name)
                    if project_data.entry_point_directory in file_path and not exclude_check(dname, file_path):
                        cobol_merger.generate_club_pairs([file_name, dname], tech=project_data.technology)
                        file_metadata = repo_metadata.get(Path(file_path).as_posix(), dict())
                        run_files_dict[file_path] = [run_id, file_path, file_metadata]
        cobol_merger.create_merge_file()
        exclude_files = cobol_merger.files_to_exclude
        for file_path in run_files_dict.keys():
            if file_path not in exclude_files:
                run_file_obj = run_files_dict.get(file_path)
                run_files.append(CodeAnalysisRunFile(code_analysis_run_id=run_file_obj[0], file_path=run_file_obj[1],
                                                     file_metadata=run_file_obj[2]))

        for file_name, src_skel_pair in cobol_merger.clubbed_set.items():
            clubbed_file_path = os.path.join(src_skel_pair[0][1], f'{file_name} listing.txt')
            file_metadata = repo_metadata.get(Path(clubbed_file_path).as_posix(), dict())
            run_files.append(CodeAnalysisRunFile(code_analysis_run_id=run_id,
                                                 file_path=clubbed_file_path, file_metadata=file_metadata))
        if run_files:
            inserted_file_ids = di[CodeAnalysisRunFileRepository].insert_code_analysis_run_file(run_files)
            if IngestionStage.PARSE in ingestion_stage_info.get("selected_stage"):
                sender_cb(queue_name=os.getenv("FILE_PARSE_QUEUE_NAME"), message_body=inserted_file_ids)
                    

        di[CodeAnalysisRunService].update_status(run_id, "File discovery Completed")

        neo_service = di[NeoModelService]
        neo_service.create_project_node(project, project_data, run_id)

        for group in project_data.functional_modules:
            user_verified_groups = UserVerifiedGroups(
                name=group['name'].strip(),
                project_id=project.id,
                run_id = run_id,
                description=group['description'],
            )
            user_verified_groups.save()


    @staticmethod
    def __clone_repo(technology: str, branch: str, repo_url: str, run_id: int):
        try:
            di[CodeAnalysisRunService].update_status(run_id, "Cloning InProgress")

            repo_data, cloned_path = RepoLoader().load_repository(
                technology=technology,
                branch=branch,
                repo_url=repo_url
            )
            return repo_data, cloned_path
        except Exception as e:
            di[CodeAnalysisRunService].update_status(run_id, "Cloning Failed")
            raise Exception(e.with_traceback(e.__traceback__))

