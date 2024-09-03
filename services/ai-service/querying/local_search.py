import asyncio
import os
import yaml
import dotenv
import pandas as pd
import tiktoken

from supabase import create_client, Client

from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.input.loaders.dfs import (
    store_entity_semantic_embeddings,
)
from graphrag.query.llm.oai.chat_openai import ChatOpenAI
from graphrag.query.llm.oai.embedding import OpenAIEmbedding
from graphrag.query.llm.oai.typing import OpenaiApiType
from graphrag.query.question_gen.local_gen import LocalQuestionGen
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore

from models.graphrag_search import LocalSearchResult

dotenv.load_dotenv()

SWEDEN_AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

async def local_asearch(query: str, project_name: str) -> LocalSearchResult:
    """
    Search a knowlege graph for a given query using the local search technique.
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
    local_search_config = config["local_search"]

    entity_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_nodes.parquet") # might be wrong path?
    entity_df = pd.read_parquet(entity_file)
    
    entity_embedding_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_entities.parquet")
    entity_embedding_df = pd.read_parquet(entity_embedding_file)

    entities = read_indexer_entities(entity_df, entity_embedding_df, root_config['community_level'])

    # Load description embeddings to an in-memory lancedb vectorstore
    description_embedding_store = LanceDBVectorStore(
        collection_name="entity_description_embeddings",
    )
    description_embedding_store.connect(db_uri=root_config['lancedb_uri'])
    
    entity_description_embeddings = store_entity_semantic_embeddings(
        entities=entities, vectorstore=description_embedding_store
    )

    
    relationship_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_relationships.parquet")
    relationship_df = pd.read_parquet(relationship_file)
    relationships = read_indexer_relationships(relationship_df)

    reports_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_community_reports.parquet")
    report_df = pd.read_parquet(reports_file)
    reports = read_indexer_reports(report_df, entity_df, root_config['community_level'])

    text_units_file = supabase.storage.from_('knowledge_graphs').download(f"/{project_name}/create_final_text_units.parquet")
    text_unit_df = pd.read_parquet(text_units_file)
    text_units = read_indexer_text_units(text_unit_df)

    llm_params = local_search_config["llm_params"]

    llm = ChatOpenAI(
        api_key=SWEDEN_AZURE_API_KEY,
        model="gpt-4o",
        api_base="https://startino.openai.azure.com/",
        api_version="2023-03-15-preview",
        api_type=OpenaiApiType.AzureOpenAI,  # OpenaiApiType.OpenAI or OpenaiApiType.AzureOpenAI
        max_retries=20,
    )

    token_encoder = tiktoken.get_encoding("cl100k_base")

    text_embedder = OpenAIEmbedding(
        api_key=OPENAI_API_KEY,
        api_type=OpenaiApiType.OpenAI,
        model=local_search_config["embedding_model"],
        max_retries=20,
    )

    context_builder = LocalSearchMixedContext(
        community_reports=reports,
        text_units=text_units,
        entities=entities,
        relationships=relationships,
        # if you did not run covariates during indexing, set this to None
        covariates=None,
        entity_text_embeddings=description_embedding_store,
        embedding_vectorstore_key=EntityVectorStoreKey.ID,  # if the vectorstore uses entity title as ids, set this to EntityVectorStoreKey.TITLE
        text_embedder=text_embedder,
        token_encoder=token_encoder,
    )

    search_engine = LocalSearch(
        llm=llm,
        context_builder=context_builder,
        token_encoder=token_encoder,
        llm_params=llm_params,
        context_builder_params=local_search_config["local_context_params"],
        response_type=local_search_config["response_type"],  # free form text describing the response type and format, can be anything, e.g. prioritized list, single paragraph, multiple paragraphs, multiple-page report
    )

    result = await search_engine.asearch(query)
    
    return LocalSearchResult(
        query=query,
        response=result.response,
        reports=str(result.context_data["reports"]),
        llm_calls=result.llm_calls,
        prompt_tokens=result.prompt_tokens,
    )
