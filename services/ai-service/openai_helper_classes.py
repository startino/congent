import os
import dotenv
from langchain_openai import AzureChatOpenAI, ChatOpenAI

dotenv.load_dotenv()

AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def new_azure_llm():
    return AzureChatOpenAI(
    api_key=AZURE_API_KEY,
    deployment_name="gpt-4o",
    model="gpt-4o",
    azure_endpoint="https://startino.openai.azure.com/",
    api_version="2024-02-01",
    max_retries=20,
)

def new_openai_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o",
        temperature=0,
    )
