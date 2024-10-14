import os


def convert_markdown_to_html(
        md_file_path: str,
        output_path: str,
    ):
    """Convert a Markdown string to a PDF file using npx command.

    Args:
        md_file_path (str): The Markdown string to convert.
        output_path (str): The path to save the PDF file.
        output_format (str): The output format to use (html or pdf).
    """

    # Convert the markdown file to PDF
    command = f"""
        npx @marp-team/marp-cli \
            {md_file_path} \
            --theme marp_themes/custom.css \
            --allow-local-files \
            --html \
            -o {output_path}
    """

    os.system(command)