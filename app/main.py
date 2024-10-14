import os
import glob
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.services.s3_file_handler import S3FileHandler
from app.services.llm_handler import LLMHandler
from app.services.markdown_handler import convert_markdown_to_html
from app.services.read_pdf import read_pdf, save_text
from app.services.create_prompt import create_system_prompt
from app.db.models.summary_pages import SummaryPage
from app.config import config

load_dotenv("config/.env")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost", "http://localhost:3000"]}})


format_check_llm_system_prompt = f"""
    あなたは優秀な翻訳者兼フォーマッター。
    与えられた英語もしくは日本語のMarpフォーマットのスライド内容を、
    以下の規則に従って日本語に翻訳して：

    - 出力は"---"から始めること
    - テンプレートのMarp header, titleスライドはない場合には適切に追加すること
    - スライドのタイトルと著者名は翻訳せず、元の英語のままにすること
    - スライドに関係のない文章は削除すること
    - それ以外のすべての内容を日本語に翻訳すること
    - 技術用語や固有名詞は適切に扱うこと
    - 翻訳後も元の意味を正確に保持すること
    - 日本語として自然で読みやすい文章にすること
    - 「である調」で翻訳すること
"""


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

            # Create prompt
            system_prompt = create_system_prompt(
                config.PROMPT_TEMPLATE_PATH,
                config.MARP_TEMPLATE_PATH,
                config.CSS_TEMPLATE_PATH,
            )

            # Prepare LLM
            paper_summary_llm = LLMHandler(
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS,
                top_p=config.TOP_P
            )

            content_prompt = f"pdfは以下の通り： \n\n{pdf_text}"

            # Generate summary
            output = paper_summary_llm.generate(system_prompt, content_prompt)

            # Format check LLM
            format_check_llm = LLMHandler(
                temperature=0.3,
                max_tokens=6000,
                top_p=0.95
            )

            output = format_check_llm.generate(
                format_check_llm_system_prompt, 
                f"Marpコンテンツは以下の通り：\n\n{output}"
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