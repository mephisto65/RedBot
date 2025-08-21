import os
import requests
from langchain_core.tools import tool
import time

@tool
def download_file_tool(url: str) -> str:
    """
    Download any type of file from a given URL and save it to 'retrieve_files/'.
    Handles URLs without filenames or extensions using the MIME type.

    Args:
        url: URL of the file to download.

    Returns:
        A message indicating success or failure.
    """
    folder_path = "retrieve_files/"
    os.makedirs(folder_path, exist_ok=True)

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Try to get the filename from Content-Disposition header
        cd = response.headers.get('content-disposition')
        if cd and 'filename=' in cd:
            filename = cd.split('filename=')[1].strip(' "')
        else:
            # Fallback: take last part of URL
            filename = url.split("/")[-1].split("?")[0]

        # If filename has no extension, guess from content-type
        if "." not in filename:
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" in content_type:
                filename += ".pdf"
            else:
                # Generic fallback
                filename += ".bin"

        file_path = os.path.join(folder_path, filename)

        # Save file
        with open(file_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"File downloaded successfully: {file_path}"

    except Exception as e:
        return f"Error downloading file: {str(e)}"


# # Test
# if __name__ == "__main__":
#     print(download_file_tool("https://arxiv.org/pdf/1808.01162"))
