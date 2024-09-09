from io import BytesIO
import os

import dotenv
import pandas as pd
from pyarrow import BufferReader
from supabase import create_client, Client

dotenv.load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = create_client(url, key)


# file_bytes = supabase.storage.from_('knowledge_graphs').download(f"/readai_aug_8/create_final_nodes.parquet")
# print(type(file_bytes))

# # Convert bytes to BytesIO
# file_buffer = BytesIO(file_bytes)

# entity_df = pd.read_parquet(file_bytes)

# print(entity_df.head())
