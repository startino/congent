import getpass
import os

import dotenv
from langchain_community.graphs import Neo4jGraph
from langchain_core.documents import Document

from langchain_core.documents import Document

from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI


dotenv.load_dotenv()

os.environ["NEO4J_URI"] = "bolt://localhost:7687"
os.environ["NEO4J_USERNAME"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "salute-april-easy-support-welcome-4272"

graph = Neo4jGraph()

llm = ChatOpenAI(temperature=0, model_name="gpt-4o")

llm_transformer = LLMGraphTransformer(llm=llm, node_properties=True)

folder_path = "./sample_readai_data"

documents = []

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    with open(file_path, "r") as file:
        text = file.read()
        documents.append(Document(page_content=text))
        
graph_documents = llm_transformer.convert_to_graph_documents(documents)

for document in graph_documents:
    print(f"Nodes:{document.nodes}")
    print(f"Relationships:{document.relationships}")
    print("\n")

