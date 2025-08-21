import fitz  # PyMuPDF
from langchain_core.tools import tool

@tool
def read_pdf(input_str: str) -> str:
    """
    Reads a PDF according to the format '/path/file.pdf|start_page|end_page'.

    Args:
        input_str: String with the PDF path and the page range.

    Returns:
        Extracted text from the PDF.
    """
    try:
        file_path, start_page, end_page = input_str.split("|")
        start_page = int(start_page)
        end_page = int(end_page)
    except ValueError:
        return "Invalid format. Use '/path/file.pdf|start_page|end_page'."

    doc = fitz.open(file_path)
    text_output = ""

    for page_num in range(start_page, end_page + 1):
        if 1 <= page_num <= doc.page_count:
            page = doc.load_page(page_num - 1)
            text_output += f"\n--- Page {page_num} ---\n"
            text_output += page.get_text()
        else:
            text_output += f"\n--- Page {page_num} invalid (out of range) ---\n"

    doc.close()
    return text_output

# # Example usage
# if __name__ == "__main__":
#     input_str = "retrieve_files/1808.01162v1.pdf|1|1"
#     text = read_pdf.invoke(input_str)
#     print(text)

import os

@tool
def read_txt(file_path: str, max_chars: int = 5000) -> str:
    """
    Reads a text/plain file and returns its content.

    Args:
        file_path: path to the text file
        max_chars: character limit to avoid reading very large files

    Returns:
        Content of the file as plain text
    """
    if not os.path.exists(file_path):
        return f"Error: file {file_path} does not exist."

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
            if f.read(1):  # if the file is longer
                content += "\n\n[⚠️ Output truncated - file too large]"
        return content
    except Exception as e:
        return f"Error while reading: {str(e)}"


# # Example usage
# if __name__ == "__main__":
#     print(read_txt.invoke("retrieve_files/example.config"))



