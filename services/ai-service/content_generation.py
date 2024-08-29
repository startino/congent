import os

from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY is not set")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    
    
graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o")

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

graph_builder.add_node(chatbot, "chatbot")

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

print(graph.get_graph().draw_mermaid())

while True:
    user_input = input("User: ")
    if user_input.lower() in ["q", "exit", "quit"]:
        print("Goodbye!")
        break
    for event in graph.stream({"messages": user_input}):
        for value in event.values():
            print("Chatbot: ", value["messages"][-1].content)