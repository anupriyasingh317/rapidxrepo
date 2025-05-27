from enum import Enum


class IngestionStage(str, Enum):
    PARSE = "parse"
    LINKING = "function_linker"
    ANALYSE = "code_analyser"
    INSIGHTS = "insights_generator"
