# Python code to export a PostgreSQL database to a CSV file
from dotenv import load_dotenv

load_dotenv()
import os
#import psycopg2
import csv
import logging
import sys
#REPLACE WITH YOUR OWN PATH
sys.path.append(r"C:\Users\2000141793\PycharmProjects\ParserCode\app-codescout\Parser2.0\repository_analyser_service")
from models.postgres.prompt_catalog import PromptCatalog
#from utils.postgres_utils import get_session
from typing import List
from datetime import datetime, timezone

from repositories.prompt_catalog_repository import PromptCatalogRepository
from repositories.project_prompt_catalog_repository import ProjectPromptCatalogRepository
from services.prompt_catalog_service import PromptCatalogService



from kink import inject, di
_LOGGER = logging.getLogger("snippetanalyser")
MODEL_PROVIDER = os.environ["MODEL_PROVIDER"]
UTC = timezone.utc


# CSV file path
# PLACE YOUR OWN LOCAL FILE PATH THERE
CSV_FILE_PATH = r"C:\Users\2000141793\Downloads\master_prompt_catalog\updated_prompts.csv"
PROMPT_CATALOG_BACKUP= r"C:\Users\2000141793\Downloads\master_prompt_catalog\prompt_catalog_backup.csv"
CSV_FILE_PATH_WO_HEADERS = r"C:\Users\2000141793\Downloads\master_prompt_catalog\updated_prompts_wo_headers.csv"

@inject()
class PromptCatalogOperation:
    def export_prompt_catalog_to_csv_without_column_headers(self, tech):
        _LOGGER.info("Copying prompts to csv...")
        try:
            prompts = di[PromptCatalogRepository].get_all_prompt_for_tech(tech=tech)
            print(len(prompts))   #, " Type: ", type(prompts))
            #print(type(prompts[0]))
            column_names = [column.name for column in PromptCatalog.__table__.columns]
            #print(column_names)

            # Write to CSV
            with open(CSV_FILE_PATH_WO_HEADERS, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                #writer.writerow(column_names)
                print("Total prompts: ", len(prompts))
                for prompt in prompts:
                    writer.writerow([getattr(prompt, column) for column in column_names])
            _LOGGER.info("Prompts written to csv successfully!")

        except Exception as e:
            _LOGGER.error(self, e)

    def export_all_prompt_catalog_with_headers(self):
        _LOGGER.info("Copying prompts to csv...")
        try:
            prompts = di[PromptCatalogRepository].get_all_prompt_catalog()
            print(len(prompts))   #, " Type: ", type(prompts))
            column_names = [column.name for column in PromptCatalog.__table__.columns]
            #print(column_names)

            # Write to CSV
            with open(PROMPT_CATALOG_BACKUP, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(column_names)
                print("Total prompts: ", len(prompts))
                for prompt in prompts:
                    writer.writerow([getattr(prompt, column) for column in column_names])
            _LOGGER.info("Prompts written to csv successfully!")


        #print("Models have been dumped to models.csv")
        except Exception as e:
            _LOGGER.error(self, e)


    def copy_prompt_catalog_to_csv(self, tech):
        """
        This method exports the prompt catalog table for the provided technology
        to a csv file with column headers as first row
        """
        _LOGGER.info("Copying prompts to csv...")
        try:
            prompts = di[PromptCatalogRepository].get_all_prompt_for_tech(tech=tech)
            print(len(prompts))   #, " Type: ", type(prompts))
            column_names = [column.name for column in PromptCatalog.__table__.columns]
            #print(column_names)

            # Write to CSV
            with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(column_names)
                print("Total prompts: ", len(prompts))
                for prompt in prompts:
                    writer.writerow([getattr(prompt, column) for column in column_names])
            _LOGGER.info("Prompts written to csv successfully!")

        except Exception as e:
            _LOGGER.error(self, e)

    def truncate_table_prompt_catalog(self):
        di[PromptCatalogRepository].truncate_prompt_catalog()
        _LOGGER.info("Prompt catalog Table truncated successfully!")
        print("Prompt catalog Table truncated successfully!")

    def delete_from_table_project_prompt_catalog(self, project_id):
        print("Deleting from ", project_id)
        di[ProjectPromptCatalogRepository].delete_prompts_of_project(project_id)
        print("Deleted prompts from project prompt catalog for project id: ", project_id)

    def import_prompt_catalog_from_csv_without_redis_refresh(self):
        """
            This Method follows the following steps:
            1. Truncate cascade prompt catalog table
            2. Import from csv to prompt catalog table. The csv file should contain column names as first row
        """
        #first step truncate cascade prompt catalog table
        self.truncate_table_prompt_catalog()
        #Import from csv to prompt catalog table
        print("Importing to prompt catalog from csv")
        project_prompts: List[PromptCatalog] = []
        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                # Insert each row into the table
                for row in csvreader:
                    project_prompt = PromptCatalog(
                        id= row['id'],
                        provider= row['provider'],
                        technology= row['technology'],
                        type= row['type'],
                        attribute= row['attribute'],
                        text= row['text'],
                        created_by= row['created_by'],
                        created_date=  row['created_date'],
                        updated_by= row['updated_by'],
                        updated_date= row['updated_date'],
                        MatchAttribute= 'N/A' if not row['MatchAttribute'] else row['MatchAttribute'],
                        MatchAttributeValue=  'N/A' if not row['MatchAttributeValue'] else row['MatchAttributeValue']
                    )
                    project_prompts.append(project_prompt)

                    di[PromptCatalogRepository].insert_prompt_catalog(project_prompts)
            _LOGGER.info(f"Prompt catalog updated successfully with {len(project_prompts)} rows!")
        except Exception as e:
            _LOGGER.error(f"ERROR OCCURRED! {e}")

    def import_prompt_catalog_wo_header(self):
        """
        THIS WILL IMPORT PROMPT CATALOG CSV FILE WITHOUT HEADER.
        REFRAIN FROM USING THIS AS IS UNSAFE TO IMPORT THIS WITHOUT COLUMN NAMES
        """
        #first step truncate cascade prompt catalog table
        self.truncate_table_prompt_catalog()

        # Import from csv to prompt catalog table
        print("Importing to prompt catalog from csv")
        project_prompts: List[PromptCatalog] = []
        counter= 0
        current_time = datetime.now(UTC)
        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.reader(csvfile)
                # Insert each row into the table
                for row in csvreader:
                    counter += 1
                    project_prompt = PromptCatalog(
                    id=row[0],
                    provider=row[1],
                    technology=row[2],
                    type=row[3],
                    attribute=row[4],
                    text=row[5],
                    created_by=row[6],
                    created_date=current_time,
                    updated_by=row[8],
                    updated_date=current_time,
                    MatchAttribute='N/A' if not row[10] else row[10],
                    MatchAttributeValue='N/A' if not row[11] else row[11]
                )
                    project_prompts.append(project_prompt)
                    if counter == 5:
                        break


            di[PromptCatalogRepository].insert_prompt_catalog(project_prompts)

            _LOGGER.info(f"Prompt catalog updated successfully with {len(project_prompts)} rows!")
        except Exception as e:
            print(f"Error occurred {e}")


    def delete_project_prompt_refresh_redis(self, project_id, tech):
        # DELETE FROM PROJECT_PROMPT_CATALOG_TABLE for the project_id
        self.delete_from_table_project_prompt_catalog(project_id)

        # CAll the prompt_catalog_service
        print(f"Calling prompt catalog service for project_id: {project_id} and {tech}")
        di[PromptCatalogService].load_prompt_catalog_for_project(project_id, tech)

    def import_prompt_catalog_from_csv(self):
        """
            This Method follows the following steps:
            1. Truncate cascade prompt catalog table
            2. Import from csv to prompt catalog table. The csv file should contain column names as first row

        """
        current_time = datetime.now(UTC)
        #first step truncate cascade prompt catalog table
        self.truncate_table_prompt_catalog()
        #Import from csv to prompt catalog table
        print("Importing to prompt catalog from csv")
        project_prompts: List[PromptCatalog] = []
        try:
            with open(CSV_FILE_PATH, 'r', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)
                # Insert each row into the table
                for row in csvreader:
                    project_prompt = PromptCatalog(
                        id= row['id'],
                        provider= row['provider'],
                        technology= row['technology'],
                        type= row['type'],
                        attribute= row['attribute'],
                        text= row['text'],
                        created_by= row['created_by'],
                        created_date= current_time, #row['created_date'],
                        updated_by= row['updated_by'],
                        updated_date=  current_time, #row['updated_date'],
                        MatchAttribute= 'N/A' if not row['MatchAttribute'] else row['MatchAttribute'],
                        MatchAttributeValue=  'N/A' if not row['MatchAttributeValue'] else row['MatchAttributeValue']
                    )
                    project_prompts.append(project_prompt)

                di[PromptCatalogRepository].insert_prompt_catalog(project_prompts)
            _LOGGER.info(f"Prompt catalog updated successfully with {len(project_prompts)} rows!")

        except Exception as e:
            _LOGGER.error(f"ERROR OCCURRED! {e}")

#if __name__ == '__main__':
    #BACK UP THE ENTIRE PROMPT CATALOG TABLE
    #PromptCatalogOperation().export_all_prompt_catalog_with_headers()

     #PromptCatalogOperation().copy_prompt_catalog_to_csv('natural')
     #PromptCatalogOperation().import_prompt_catalog_from_csv()
     #PromptCatalogOperation().delete_project_prompt_refresh_redis(1471, 'natural')



     #1471- test project



