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
