import asyncio
from querying.global_search import global_search

query = "What is Jorge?"
asyncio.run(global_search(query))