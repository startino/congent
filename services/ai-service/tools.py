import asyncio

from langchain_core.tools import tool

from querying.global_asearch import global_asearch
from querying.local_asearch import local_asearch


@tool
def search_graph(query: str) -> str:
    """
    Search a knowlege graph for a given query.
    It uses an LLM agent to search the graph and return the results,
    which is why as much context as possible should be provided in the query.
    We do not value reducing the query length.
    
    Args:
        query (str): The query to search the graph. Should provide as much
        context as possible.
        
    """
    
    async def run_searches():
        global_task = global_asearch(query, "readai_aug_8")
        local_task = local_asearch(query, "readai_aug_8")
        global_result, local_result = await asyncio.gather(global_task, local_task)
        return global_result, local_result
    
    global_result, local_result = asyncio.run(run_searches())
    
    final_result = f"""
    The RAG Agent has returned the following results:
    
    -Global Search Result-
    {global_result.response}
    
    -Local Search Result-
    {local_result.response}
    """
    return final_result