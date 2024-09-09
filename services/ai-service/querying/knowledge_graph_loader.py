from io import BytesIO
from supabase import Client
import pandas as pd

class KnowledgeGraphLoader:
    def __init__(self, project_name: str, supabase: Client):
        # code for when profile and project management is setup on frontend
        # self._profile_id = profile_id
        # self._project_id = project_id
        self._project_name = project_name
        self._supabase = supabase
        self._entity_df = None
        self._entity_embedding_df = None
        self._relationship_df = None
        self._report_df = None
        self._text_unit_df = None

    def _load_parquet(self, file_path: str):
        # code for when profile and project management is setup on frontend
        # file_bytes = self._supabase.storage.from_('knowledge_graphs').download(f"{self._profile_id}/{self._project_id}/file_path")
        file_bytes = self._supabase.storage.from_('knowledge_graphs').download(f"{self._project_name}/{file_path}")
        if file_bytes is None:
            raise FileNotFoundError(f"File not found: {file_path}")
        file_buffer = BytesIO(file_bytes)
        return pd.read_parquet(file_buffer)

    @property
    def entity_df(self):
        if self._entity_df is None:
            self._entity_df = self._load_parquet("/create_final_nodes.parquet")
        return self._entity_df

    @property
    def entity_embedding_df(self):
        if self._entity_embedding_df is None:
            self._entity_embedding_df = self._load_parquet("/create_final_entities.parquet")
        return self._entity_embedding_df

    @property
    def relationship_df(self):
        if self._relationship_df is None:
            self._relationship_df = self._load_parquet("/create_final_relationships.parquet")
        return self._relationship_df

    @property
    def report_df(self):
        if self._report_df is None:
            self._report_df = self._load_parquet("/create_final_community_reports.parquet")
        return self._report_df

    @property
    def text_unit_df(self):
        if self._text_unit_df is None:
            self._text_unit_df = self._load_parquet("/create_final_text_units.parquet")
        return self._text_unit_df