import os
import dotenv
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.typing import OpenaiApiType

dotenv.load_dotenv()

SWEDEN_AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
EASTUS_AZURE_API_KEY = os.getenv("EASTUS_AZURE_API_KEY")

east_us_llm = ChatOpenAI(
        api_key=EASTUS_AZURE_API_KEY,
        model="gpt-4o",
        api_base="https://startino-eastus.openai.azure.com/",
        api_version="2023-03-15-preview",
        api_type=OpenaiApiType.AzureOpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )
    
sweden_llm = ChatOpenAI(
        api_key=SWEDEN_AZURE_API_KEY,
        model="gpt-4o",
        api_base="https://startino.openai.azure.com/",
        api_version="2023-03-15-preview",
        api_type=OpenaiApiType.AzureOpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )