import boto3
from langchain.schema import SystemMessage, HumanMessage
from langchain_community.chat_models import BedrockChat

from app.config import config


class LLMHandler():

    def __init__(self, temperature: float, max_tokens: int, top_p: float):
        bedrock_client = self.initialize_bedrock_client()
        self.llm = BedrockChat(
            client=bedrock_client,
            model_id=config.MODEL_NAME,
            model_kwargs={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p
            },
            region_name=config.AWS_DEFAULT_REGION,
        )

    def initialize_bedrock_client(self):
        bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=config.AWS_DEFAULT_REGION,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
        )
        return bedrock_client

    def generate(
            self,
            system_prompt: str,
            custom_prompt: str
        ) -> str:

        # メッセージを適切なフォーマットで作成
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=custom_prompt)
        ]

        # LLMを直接呼び出し
        response = self.llm.invoke(messages)
        return response.content


class LLMAgent(LLMHandler):
    def __init__(
            self, 
            name: str, 
            temperature: float, 
            max_tokens: int, 
            top_p: float
    ):
        super().__init__(temperature, max_tokens, top_p)
        self.system_prompt = ""
        self.custom_prompt = ""
        self.name = name

    def set_system_prompt(self, system_prompt_path: str):
        with open(system_prompt_path, 'r') as file:
            self.system_prompt = file.read()
    
    def set_custom_prompt(self, custom_prompt_path: str):
        with open(custom_prompt_path, 'r') as file:
            self.custom_prompt = file.read()
    
    def response(self, user_input: str) -> str:
        return self.generate(self.system_prompt, user_input)
