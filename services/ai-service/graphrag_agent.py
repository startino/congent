import os
import asyncio
import dotenv
from typing import Annotated, Literal, TypedDict

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from psycopg_pool import ConnectionPool

from querying.global_search import global_asearch
from querying.local_search import local_asearch
from models import GlobalSearchResult, LocalSearchResult
from openai_helper_classes import new_openai_llm

dotenv.load_dotenv()

AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_URI = os.getenv("DB_URI")

@tool
def search_graph(query: str) -> GlobalSearchResult:
    """
    Search a knowlege graph for a given query.
    It uses an LLM agent to search the graph and return the results,
    which is why as much context as possible should be provided in the query.
    We do not value reducing the query length.
    
    Args:
        query (str): The query to search the graph. Should provide as much
        context as possible.
    """
    
    global_result: GlobalSearchResult = asyncio.run(global_asearch(query))
    local_result: LocalSearchResult = asyncio.run(local_asearch(query))
    
    final_result = f"""
    The RAG Agent has returned the following results:
    
    -Global Search Result-
    {global_result.response}
    
    -Local Search Result-
    {local_result.response}
    """
    return final_result


connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

pool = ConnectionPool(
    conninfo=DB_URI,
    max_size=20,
    kwargs=connection_kwargs,
)

print("file called")


def invoke(thread_id: str, user_message: str):
    tools = [search_graph]

    tool_node = ToolNode(tools)

    openai_llm = new_openai_llm()


    llm = openai_llm.bind_tools(tools)

    inputs = {"messages": [("user", user_message)]}

    config = {"configurable": {"thread_id": thread_id}}

    with pool.connection() as conn:
        print("\n Connected to the database... \n")
        checkpointer = PostgresSaver(conn)

        # NOTE: you need to call .setup() the first time you're using your checkpointer
        # checkpointer.setup()
        graph = create_react_agent(llm, tools=tools, checkpointer=checkpointer)
        
        res = graph.invoke(inputs, config)
        
        new_checkpoint = checkpointer.get(config)

    return res, new_checkpoint

# pnpm dlx supabase --experimental --project-ref oampjdurcoprcjifbnhn postgres-config update --config max_connections=120
