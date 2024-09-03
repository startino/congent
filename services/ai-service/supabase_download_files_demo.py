import os

import dotenv
from supabase import create_client, Client

dotenv.load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)

res = supabase.storage.list_buckets()

print(res)

res = supabase.storage.from_('knowledge_graphs').list()

print(res)

with open("./supabase_file.csv", 'wb+') as f:
  res = supabase.storage.from_('knowledge_graphs').download("/readai_aug_8/create_final_community_reports.csv")
  f.write(res)
