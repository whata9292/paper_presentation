import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../config/.env')

class Config:
    # Agent settings
    AGENT_SETTINGS_PATH = os.getenv('AGENT_SETTINGS_PATH', 'templates/agent_settings.yaml')

    # OpenAI settings
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '8192'))
    TOP_P = float(os.getenv('TOP_P', '0.95'))

    # Claude settings
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

    # Model settings
    MODEL_NAME = os.getenv('MODEL_NAME', 'anthropic.claude-3-haiku-20240307-v1:0')

    # AWS settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')

    # File paths
    PROMPT_TEMPLATE_PATH = os.getenv('PROMPT_TEMPLATE_PATH', 'templates/prompt_summary_generator.txt')
    MARP_TEMPLATE_PATH = os.getenv('MARP_TEMPLATE_PATH', 'marp_themes/template.md')
    CSS_TEMPLATE_PATH = os.getenv('CSS_TEMPLATE_PATH', 'marp_themes/custom.css')
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'temp')

    # S3 settings
    S3_BUCKET_NAME = 'marp-presentation'
    S3_DOWNLOAD_FOLDER_DIR = 'raw_files'
    S3_UPLOAD_FOLDER_DIR = 'paper'

    # CloudFront settings
    CLOUDFRONT_URL = os.getenv('CLOUDFRONT_URL', 'https://d2is53fus238ee.cloudfront.net')

    @classmethod
    def update(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)

# Initialize default config
config = Config()