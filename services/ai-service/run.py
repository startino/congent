import asyncio
from querying.global_search import global_search
from querying.local_search import local_search

query = "What operation system does jorge use"
local_search_result = local_search(query)
global_search_result = global_search(query)

print(f"-LOCAL SEARCH RESULT- \n {local_search_result.response} \n\n")
print(f"-GLOBAL SEARCH RESULT- \n {global_search_result.response}")