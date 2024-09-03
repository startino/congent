import asyncio

from querying import run_both_asearches

query = "What operation system does jorge use"

global_result, local_result = asyncio.run(run_both_asearches("graphrag", query,))

print(f"-GLOBAL SEARCH RESULT- \n {global_result.response}")
print(f"-LOCAL SEARCH RESULT- \n {local_result.response} \n\n")
