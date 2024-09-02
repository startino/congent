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

dotenv.load_dotenv()

api_key = os.getenv("SWEDEN_AZURE_API_KEY")

async def global_asearch(query: str)-> GlobalSearchResult:
    """
    Search a knowlege graph for a given query using the global search technique.
    The configuration for the local search is loaded from a local config file
    and can be modified there.
    """
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.yml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    root_config = config["root"]
    global_search_config = config["global_search"]
        
    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o",
        api_base="https://startino.openai.azure.com/",
        api_version="2023-03-15-preview",
        api_type=OpenaiApiType.AzureOpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")

    entity_df = pd.read_parquet(f"{root_config['input_dir']}/{root_config['entity_table']}.parquet")
    report_df = pd.read_parquet(f"{root_config['input_dir']}/{root_config['community_report_table']}.parquet")
    entity_embedding_df = pd.read_parquet(f"{root_config['input_dir']}/{root_config['entity_embedding_table']}.parquet")

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