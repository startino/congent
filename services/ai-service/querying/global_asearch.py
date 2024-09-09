import asyncio
import json
import os
import logging

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
from .knowledge_graph_loader import KnowledgeGraphLoader
from .llm_helpers import east_us_llm

from supabase import create_client, Client

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


async def global_asearch(query: str, project_name: str) -> GlobalSearchResult:
    """
    Search a knowledge graph for a given query using the global search technique.
    The configuration for the local search is loaded from a local config file
    and can be modified there.
    
    Args:
        query (str): The query to search the graph. Should provide as much
        context as possible.
        project_name (str): The name of the project's storage bucket on Supabase.
    """
    
    logger.info("Starting search for query: %s", query)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "config.yml")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    root_config = config["root"]
    global_search_config = config["global_search"]

    token_encoder = tiktoken.get_encoding("cl100k_base")
    
    loader = KnowledgeGraphLoader(project_name, supabase)
    
    logger.info("Loading knowledge graph data")
    entities = read_indexer_entities(loader.entity_df, loader.entity_embedding_df, root_config['community_level'])
    reports = read_indexer_reports(loader.report_df, loader.entity_df, root_config['community_level'])
    
    logger.info("Knowledge graph data loaded successfully")

    context_builder = GlobalCommunityContext(
        community_reports=reports,
        entities=entities,  # default to None if you don't want to use community weights for ranking
        token_encoder=token_encoder,
    )

    context_builder_params = global_search_config["context_builder_params"]
    map_llm_params = global_search_config["map_llm_params"]
    reduce_llm_params = global_search_config["reduce_llm_params"]

    search_engine = GlobalSearch(
        llm=east_us_llm,
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

    logger.info("Starting search engine")
    result = await search_engine.asearch(query)
    logger.info("Search completed successfully")

    return GlobalSearchResult(
        query=query,
        response=result.response,
        reports=str(result.context_data["reports"]),
        llm_calls=result.llm_calls,
        prompt_tokens=result.prompt_tokens,
    )

if __name__ == "__main__":
    # You'll get an error if you run this code because of relative imports
    query = "What is Jorge?"
    asyncio.run(global_asearch(query, "readai_aug_8"))