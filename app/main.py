import os
from dotenv import load_dotenv
from app.services.s3_file_handler import S3FileHandler
from app.services.read_pdf import read_pdf, save_text
from app.services.create_prompt import create_system_prompt
from app.config import config

import boto3
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.chat_models import BedrockChat

load_dotenv("config/.env")


def initialize_bedrock_client():
    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=config.AWS_DEFAULT_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )
    return bedrock_client


def generate_summary(
        system_prompt: str,
        pdf_prompt: str
    ) -> str:
    # Initialize Claude
    bedrock_client = initialize_bedrock_client()
    llm = BedrockChat(
        client=bedrock_client,
        model_id=config.MODEL_NAME,
        model_kwargs={
            "temperature": config.TEMPERATURE,
            "max_tokens": 8192,
            # "top_p": 0.95,
        },
        region_name=config.AWS_DEFAULT_REGION,
    )

    # メッセージを適切なフォーマットで作成
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content='pdfは以下の通り： \n\n' + pdf_prompt)
    ]

    # LLMを直接呼び出し
    response = llm.invoke(messages)

    return response.content


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


def llm_format_check(
        markdown_content: str,
        markdown_template_path: str
    ) -> str:

    with open(markdown_template_path, 'r') as file:
        markdown_format = file.read()

    system_prompt = f"""
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

    marpのテンプレートは以下の通り：\n
    {markdown_format}
    """

    human_prompt = f"以下のMarpコンテンツを指示通り変更して：\n\n{markdown_content}"

    bedrock_client = initialize_bedrock_client()
    llm = BedrockChat(
        client=bedrock_client,
        model_id=config.MODEL_NAME,
        model_kwargs={
            "temperature": 0.3,
            "max_tokens": 6000,
            "top_p": 0.95,
        },
        region_name=config.AWS_DEFAULT_REGION,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    response = llm.invoke(messages)
    return response.content


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
    pdf_file_name = input("Enter the name of PDF file: ")

    # Initialize PDFFetcher
    pdf_fetcher = S3FileHandler(
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
        region_name=config.AWS_DEFAULT_REGION
    )

    # Fetch PDF from S3
    pdf_path = os.path.join('temp', pdf_file_name)
    pdf_fetcher.fetch_file(
        config.S3_BUCKET_NAME,
        config.S3_DOWNLOAD_FOLDER_DIR,
        pdf_file_name,
        pdf_path
    )

    if pdf_path:
        # Process the PDF
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        pdf_text = read_pdf(pdf_path)

        # Optionally save the extracted text
        save_text(pdf_text, f'temp/{pdf_name}.txt')

        # Create prompt
        prompt = create_system_prompt(
            config.PROMPT_TEMPLATE_PATH,
            config.MARP_TEMPLATE_PATH,
            config.CSS_TEMPLATE_PATH,
        )

        # Generate summary
        output = generate_summary(prompt, pdf_text)

        # Format check
        output = llm_format_check(output, config.MARP_TEMPLATE_PATH)

        # Write output to markdown file
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        out_md_file = os.path.join(config.OUTPUT_DIR, f'{pdf_name}.md')
        with open(out_md_file, 'w') as file:
            file.write(output)

        # Write output to markdown file
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        out_md_file = os.path.join(config.OUTPUT_DIR, f'{pdf_name}.md')
        with open(out_md_file, 'w') as file:
            file.write(output)

        # Convert markdown to PDF
        out_pdf_file = os.path.join(config.OUTPUT_DIR, f'{pdf_name}_slide.html')
        convert_markdown_to_html(out_md_file, out_pdf_file)

        pdf_fetcher.upload_file(
            out_pdf_file,
            config.S3_BUCKET_NAME,
            config.S3_UPLOAD_FOLDER_DIR,
            f'{pdf_name}_slide.html'
        )

        print(f"Summary generated and saved to {config.OUTPUT_DIR}")
    else:
        print("Failed to fetch PDF from S3.")

if __name__ == "__main__":
    main()
