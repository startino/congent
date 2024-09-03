import asyncio
import json
import os

import dotenv
import pandas as pd
import tiktoken

from graphrag.query.indexer_adapters import read_indexer_entities, read_indexer_reports
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.structured_search.global_search.community_context import (
    GlobalCommunityContext,
)
from graphrag.query.structured_search.global_search.search import GlobalSearch
import yaml

from models.graphrag_search import GlobalSearchResult

from supabase import create_client, Client

dotenv.load_dotenv()

SWEDEN_AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
EASTUS_AZURE_API_KEY = os.getenv("EASTUS_AZURE_API_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


async def global_asearch(query: str, project_name: str )-> GlobalSearchResult:
    """
    Search a knowlege graph for a given query using the global search technique.
    The configuration for the local search is loaded from a local config file
    and can be modified there.
    
    Args:
        query (str): The query to search the graph. Should provide as much
        context as possible.
        project_name (str): The name of the project's storage bucket on Supabase.
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.yml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    root_config = config["root"]
    global_search_config = config["global_search"]
        
    llm = ChatOpenAI(
        api_key=EASTUS_AZURE_API_KEY,
        model="gpt-4o",
        api_base="https://startino-eastus.openai.azure.com/",
        api_version="2023-03-15-preview",
        api_type=OpenaiApiType.AzureOpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")
    
    entity_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_nodes.parquet") # might be wrong path?
    report_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_community_reports.parquet") 
    entity_embedding_df = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_entities.parquet")
    
    entity_df = pd.read_parquet(entity_file)
    report_df = pd.read_parquet(report_file)
    entity_embedding_df = pd.read_parquet(entity_embedding_df)

    reports = read_indexer_reports(report_df, entity_df, root_config['community_level'])
    entities = read_indexer_entities(entity_df, entity_embedding_df, root_config['community_level'])

    report_df.head()

    context_builder = GlobalCommunityContext(
        community_reports=reports,
        entities=entities,  # default to None if you don't want to use community weights for ranking
        token_encoder=token_encoder,
    )

    context_builder_params = global_search_config["context_builder_params"]

    map_llm_params = global_search_config["map_llm_params"]

    reduce_llm_params = global_search_config["reduce_llm_params"]

    search_engine = GlobalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        max_data_tokens=12_000,  # change this based on the token limit you have on your model (if you are using a model with 8k limit, a good setting could be 5000)
        map_llm_params=map_llm_params,
        reduce_llm_params=reduce_llm_params,
        allow_general_knowledge=False,  # set this to True will add instruction to encourage the LLM to incorporate general knowledge in the response, which may increase hallucinations, but could be useful in some use cases.
        json_mode=True,  # set this to False if your LLM model does not support JSON mode.
        context_builder_params=context_builder_params,
        concurrent_coroutines=32,
        response_type="multiple paragraphs",  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
    )


    result = await search_engine.asearch(query)
    
    return GlobalSearchResult(
        query=query,
        response=result.response,
        reports=str(result.context_data["reports"]),
        llm_calls=result.llm_calls,
        prompt_tokens=result.prompt_tokens,
        
    )

if __name__ == "__main__":
    # You'll get an error if you run this code because the of relative imports
    query = "What is Jorge?"
    asyncio.run(global_search(query))