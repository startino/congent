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

from querying.global_search import global_search
from querying.local_search import local_search

from models import GlobalSearchResult, LocalSearchResult

dotenv.load_dotenv()

AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@tool
def search_graph(query) -> GlobalSearchResult:
    """
    Search a knowlege graph for a given query.
    It uses an agent to search the graph and return the results.
    
    Args:
        query (str): The query to search the graph. Should provide as much
        context as possible.
    
    """
    
    global_result: GlobalSearchResult = asyncio.run(global_search(query))
    local_result: LocalSearchResult = asyncio.run(local_search(query))
    
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

graph = create_react_agent(llm, tools=tools)

inputs = {"messages": [("user", "what OS does jorge use")]}

for s in graph.stream(inputs, stream_mode="values"):
    message = s["messages"][-1]
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print()