from functools import cache
from langchain_openai import AzureChatOpenAI
from core.config import config


def get_llm():
    llm = AzureChatOpenAI(
        api_version=config.OPENAI_API_VERSION,
        api_key=config.OPENAI_API_KEY,
        azure_endpoint=config.OPENAI_API_BASE,
        azure_deployment=config.OPENAI_DEPLOYMENT_NAME,
    )

    return llm