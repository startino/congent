import json
import os
import asyncio
from pprint import pprint
from uuid import UUID
import dotenv

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AnyMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from pydantic import BaseModel
from supabase import create_client, Client

from querying import run_both_asearches
from models.graphrag_search import GlobalSearchResult, LocalSearchResult
from openai_helper_classes import new_openai_llm
from memory import SupabaseChatMessageHistory
from querying.global_asearch import global_asearch
from querying.local_asearch import local_asearch
from tools import search_graph

dotenv.load_dotenv()

AZURE_API_KEY = os.getenv("SWEDEN_AZURE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DB_URI = os.getenv("DB_URI")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


async def ainvoke_graphrag_agent(session_id: UUID, user_message: str):
    
    tools = [search_graph]

    openai_llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model="gpt-4o",
        temperature=0,
        streaming=True,
    )
    
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are an agent in charge of querying a knowledge graph to retrieve information.
            You have the choice of choosing to search the graph, or reply to the user.
            You should provide as much context as possible in the query.
            When receiving the result from the tool, you should reflect on the result.
            Then you can choose to search the graph again or reply to the user.
            You may rephrase the user's query if you believe it will help.
            If the user has not given enough context, you may ask for more.
            
            GOOD Query Examples:
            query = "Tell me about Jonas"
            query = "What does Jorge think about Linux?"
            
            BAD Query Examples:
            query = "Jonas"
            query = "Jonas information"
            query = "Jorge Linux"
            query = "Jorge Linux opinion"
            """
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
    
    llm = prompt | openai_llm.bind_tools(tools)

    # Define the function that calls the model
    async def invoke_agent(state: MessagesState):
        response = await llm.ainvoke(state)
        # We return a list, because this will get added to the existing list
        return {"messages": response}

    # Define the function that determines whether to continue or not
    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        # If the last tool call was search_graph, we send it back to the agent for reflection
        if len(last_message.tool_calls) >= 1 and last_message.tool_calls[0]['name'] == "search_graph":
            return "continue"
        # Otherwise we end the conversation
        else:
            return END

    # Define a new graph
    workflow = StateGraph(MessagesState)

    # Define the two nodes we will cycle between
    workflow.add_node("agent", invoke_agent)
    workflow.add_node("tools", ToolNode(tools))

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.set_entry_point("agent")

    # We now add a conditional edge
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            END: END,
        },
    )

    # Default the tool to go back to the agent for reflection
    workflow.add_edge("tools", "agent")
    
    graph = workflow.compile()

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    message_history = SupabaseChatMessageHistory(supabase=supabase, session_id=session_id)
    
    if message_history.messages:
        last_message_in_db = message_history.messages[-1]
    else:
        last_message_in_db = None
    
    message_history.add_messages([HumanMessage(name="user",content=user_message)])

    async for event in graph.astream_events({"messages": message_history.messages}, version="v1"):
        kind = event["event"]
        # pprint(event, indent=4)
        
        # Extract the message and upload to db
        data = event.get("data", {})
        output = data.get("output")
        
        if output:
            new_message = event["data"]["output"]
            if isinstance(new_message, AnyMessage):
  
                if last_message_in_db is not None and new_message.id == last_message_in_db.id:
                    # This is caused because no new message was generated run running a node (like the supervisor node).
                    print('Duplicate message skipped successfully!');
                    continue;
                
                message_history.add_messages([new_message])
                # pprint(new_message)
        
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # print(content, end="|")
                yield content
        # elif kind == "on_tool_start":
        #     print("--")
        #     print(
        #         f"Starting tool: {event['name']} with inputs: {event['data'].get('input')}"
        #     )
        # elif kind == "on_tool_end":
        #     print(f"Done tool: {event['name']}")
        #     print(f"Tool output was: {event['data'].get('output')}")
        #     print("--")