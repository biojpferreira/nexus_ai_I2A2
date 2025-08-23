import json
import pandas as pd
from langchain.tools import tool
from pydantic import BaseModel, Field

class ConsolidateCleanInput(BaseModel):
    """
    Pydantic schema for the consolidate_and_clean_data tool input.
    """

    file_paths: str = Field(
        description="A JSON string containing the paths to the VR and VA spreadsheets."
    )

class ReadFileToolInput(BaseModel):
    file_path: str = Field(description="The full path to the file to be read.")
    file_type: str = Field(description="The type of the file, e.g., 'excel', 'csv', 'json'.")

class VRVAAutomationTools:
    """
    A collection of tools for the VR/VA calculation process.
    """

    @tool("consolidate_and_clean_data", args_schema=ConsolidateCleanInput)
    def consolidate_and_clean_data(self, file_paths: str) -> str:
        """
        Reads, merges, and cleans data from multiple spreadsheets.

        The input should be a JSON string of the file paths.
        Returns a confirmation string of the process.
        """
        try:
            # The LLM passes a JSON string; we need to parse it.
            files = json.loads(file_paths)

            # Use the file paths from the 'files' dictionary.
            print(f"Reading and consolidating files: {files}")
            # ... (rest of your pandas logic)

            # Example:
            # df_active = pd.read_excel(files["active"])

            return "Data consolidated and cleaned successfully."
        except Exception as e:
            return f"Error processing files: {e}"
    
    @tool("read_file", args_schema=ReadFileToolInput)
    def read_file(self, file_path: str, file_type: str) -> str:
        """
        Reads a file from a specified path and returns its contents.
        """
        try:
            if file_type.lower() == "excel":
                df = pd.read_excel(file_path)
                return f"File read successfully. It has {len(df)} rows and {len(df.columns)} columns."
            elif file_type.lower() == "csv":
                df = pd.read_csv(file_path)
                return f"File read successfully. It has {len(df)} rows and {len(df.columns)} columns."
            else:
                return "Error: Unsupported file type."
        except FileNotFoundError:
            return f"Error: File not found at {file_path}"
        except Exception as e:
            return f"An error occurred while reading the file: {e}"
        