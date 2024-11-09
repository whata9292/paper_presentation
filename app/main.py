import os
import glob
import yaml
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.services.s3_file_handler import S3FileHandler
from app.services.llm_handler import LLMAgent
from app.services.markdown_handler import convert_markdown_to_html
from app.services.read_pdf import read_pdf, save_text
from app.services.create_prompt import create_system_prompt
from app.db.models.summary_pages import SummaryPage
from app.config import config

load_dotenv("config/.env")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost", "http://localhost:3000"]}})


def main():
    """
    Main function to orchestrate the PDF processing workflow.

    This function performs the following steps:
    1. Get the S3 URL of the PDF file from user input.
    2. Fetch the PDF from S3.
    3. Extract text from the PDF.
    4. Generate a summary of the PDF content.
    5. Translate the summary to Japanese if it's primarily in English.
    6. Save the result as a markdown file.
    7. Convert the markdown to a PDF slide.
    """
    # Initialize PDFFetcher
    s3_file_handler = S3FileHandler(
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_DEFAULT_REGION
    )

    # Generate Agents
    with open(config.AGENT_SETTINGS_PATH, 'r') as file:
        agent_settings = yaml.safe_load(file)
    models = agent_settings['MODELS']

    for _, v in models.items():
        v['object'] = LLMAgent(
            name=v['NAME'],
            temperature=v['TEMPERATURE'],
            max_tokens=v['MAX_TOKEN_SIZE'],
            top_p=v['TOP_P']
        )
        v['object'].set_system_prompt(v['SYSTEM_PROMPT_PATH'])

    # Get the PDF file list from S3
    pdf_file_lists = s3_file_handler.get_file_lists(config.S3_BUCKET_NAME, config.S3_DOWNLOAD_FOLDER_DIR)

    for pdf_file in pdf_file_lists:
        # If pdf file is already processed and stored in db, skip
        pdf_title = os.path.splitext(pdf_file)[0]
        if SummaryPage.get_record_by_title(pdf_title) is not None:
            print(f"PDF {pdf_file} is already processed. Skipping...")
            continue

        # Fetch PDF from S3
        pdf_path = os.path.join('temp', pdf_file)
        s3_file_handler.fetch_file(
            config.S3_BUCKET_NAME,
            config.S3_DOWNLOAD_FOLDER_DIR,
            pdf_file,
            pdf_path
        )

        if pdf_path:
            # Process the PDF
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            pdf_text = read_pdf(pdf_path)

            # Optionally save the extracted text
            save_text(pdf_text, f'temp/{pdf_name}.txt')

            # Create prompt TODO: Modify PROMPT_TEMPLATE
            system_prompt = create_system_prompt(
                config.PROMPT_TEMPLATE_PATH,
                config.MARP_TEMPLATE_PATH,
                config.CSS_TEMPLATE_PATH,
            )
            models['PAPER_INTERPRETER']['object'].system_prompt = system_prompt

            user_prompt = f"pdfは以下の通り： \n\n{pdf_text}"
            # Generate summary
            summary = models['PAPER_INTERPRETER']['object'].response(user_prompt)

            output = models['FORMATTER']['object'].response( 
                f"Marpコンテンツは以下の通り：\n\n{summary}"
            )

            # Write output to markdown file
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
            out_md_file = os.path.join(config.OUTPUT_DIR, f'{pdf_name}.md')
            with open(out_md_file, 'w') as file:
                file.write(output)

            # Convert markdown to PDF
            out_pdf_file = os.path.join(config.OUTPUT_DIR, f'{pdf_name}_slide.html')
            convert_markdown_to_html(out_md_file, out_pdf_file)

            s3_file_handler.upload_file(
                out_pdf_file,
                config.S3_BUCKET_NAME,
                config.S3_UPLOAD_FOLDER_DIR,
                f'{pdf_name}_slide.html'
            )

            # Insert record into the database
            SummaryPage.insert_or_update_record(
                pdf_name, 
                f'{config.CLOUDFRONT_URL}/{config.S3_UPLOAD_FOLDER_DIR}/{pdf_name}_slide.html', 
                output
            )

            print(f"Summary generated and saved to {config.OUTPUT_DIR}")

            # Clean up files which includes file_stem in the name
            file_stem = os.path.splitext(pdf_path)[0]
            for fname in glob.glob(f'{file_stem}*'):
                os.remove(fname)

        else:
            print("Failed to fetch PDF from S3.")


@app.route('/api/process', methods=['POST'])
def process_pdf():
    print("TBA")

@app.route('/api/summary_pages', methods=['GET'])
def get_summary_pages():
    print("TBA")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)