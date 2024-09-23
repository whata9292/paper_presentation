import PyPDF2


def read_pdf(file_path: str) -> str:
    """
    Reads a PDF file and extracts its text content.

    Args:
    file_path (str): The path to the PDF file to be read.

    Returns:
    str: The extracted text from the PDF.
    """
    try:
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()

        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


def save_text(text: str, output_file: str) -> None:
    """
    Saves the given text to a file.

    Args:
    text (str): The text to be saved.
    output_file (str): The path to the output file.
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved to {output_file}")
    except Exception as e:
        print(f"Error saving text to file: {e}")
