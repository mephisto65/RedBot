import os
import zipfile
from langchain_core.tools import tool

@tool
def zip_processor_tool(filepath: str, extract_to: str = None, list_only: bool = True) -> dict:
    """
    Processes a ZIP file. You ALWAYS need to provide a valid filepath to a `.zip` archive.

    Args:
        REQUIRED : filepath (str): Path to the ZIP file.
        Optional : extract_to (str): Folder where files should be extracted. If not provided, files are not extracted.
        Optional : list_only (bool): If True, only returns the list of files inside the archive. (default: True)

    Returns:
        dict: Dictionary containing either:
            {
                "zip_file": "myarchive.zip",
                "files": ["doc.txt", "report.pdf", "config.json"]
            }
        Or (if extraction requested):
            {
                "zip_file": "myarchive.zip",
                "extracted_to": "output_folder",
                "files": ["doc.txt", "report.pdf", "config.json"]
            }
    """

    if not os.path.isfile(filepath):
        return {"error": f"❌ File not found: {filepath}"}

    result = {"zip_file": os.path.basename(filepath)}

    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            result["files"] = file_list

            if not list_only and extract_to:
                os.makedirs(extract_to, exist_ok=True)
                zip_ref.extractall(extract_to)
                result["extracted_to"] = extract_to

        return result

    except Exception as e:
        return {"error": f"❌ Failed to process ZIP: {str(e)}"}
