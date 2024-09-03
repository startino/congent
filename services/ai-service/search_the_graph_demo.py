import asyncio
from querying.global_search import global_asearch
from querying.local_search import local_asearch

query = "What operation system does jorge use"
local_search_result = asyncio.run(local_asearch(query, "readai_aug_8"))
global_search_result = asyncio.run(global_asearch(query, "readai_aug_8"))

print(f"-LOCAL SEARCH RESULT- \n {local_search_result.response} \n\n")
print(f"-GLOBAL SEARCH RESULT- \n {global_search_result.response}")