from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
import asyncio
import os
from typing import Annotated, Literal, TypedDict
import dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import create_react_agent
from querying.global_search import global_asearch
from querying.local_search import local_asearch
from models import GlobalSearchResult, LocalSearchResult
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from typing import Literal
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver

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


tools = [search_graph]

tool_node = ToolNode(tools)

azure_llm = AzureChatOpenAI(
    api_key=AZURE_API_KEY,
    deployment_name="gpt-4o",
    model="gpt-4o",
    azure_endpoint="https://startino.openai.azure.com/",
    api_version="2024-02-01",
    max_retries=20,
)

openai_llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model="gpt-4o",
    temperature=0,
)

llm = openai_llm.bind_tools(tools)

inputs = {"messages": [("user", "where is chinmay, jorge, and jonas from?")]}

config = {"configurable": {"thread_id": "41"}}

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 5,
    "keepalives_count": 5,
}

pool = ConnectionPool(
    conninfo=DB_URI,
    max_size=20,
    kwargs=connection_kwargs,
)

print(pool.check())
print(pool.get_stats())

with pool.connection() as conn:
    print("\n Connected to the database... \n")

    checkpointer = PostgresSaver(conn)

    # NOTE: you need to call .setup() the first time you're using your checkpointer
    #checkpointer.setup()
    graph = create_react_agent(llm, tools=tools, checkpointer=checkpointer)
    
    res = graph.invoke(inputs, config)
    
    checkpoint = checkpointer.get(config)
    

print("Completed.")


def invoke_agent(query):
    graph.invoke(inputs={"messages": [("user", query)]})