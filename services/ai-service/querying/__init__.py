import asyncio
from .global_asearch import global_asearch
from .local_asearch import local_asearch

async def run_both_asearches(project_name: str, query: str):
    global_task = global_asearch(project_name=project_name,query=query)
    local_task = local_asearch(project_name=project_name,query=query)
    global_result, local_result = await asyncio.gather(global_task, local_task)
    return global_result, local_result