from io import BytesIO
from supabase import Client
from pyarrow import BufferReader
import pandas as pd

class KnowledgeGraphLoader:
    def __init__(self, project_name: str, supabase: Client):
        self.project_name = project_name
        self._supabase = supabase
        self._entity_df = None
        self._entity_embedding_df = None
        self._relationship_df = None
        self._report_df = None
        self._text_unit_df = None

    @property
    def entity_df(self):
        if self._entity_df is None:
            entity_bytes = self._supabase.storage.from_('knowledge_graphs').download(f"/{self.project_name}/create_final_nodes.parquet")
            self._entity_df = pd.read_parquet(BufferReader(BytesIO(entity_bytes)))
        return self._entity_df

    @property
    def entity_embedding_df(self):
        if self._entity_embedding_df is None:
            entity_embedding_file = self._supabase.storage.from_('knowledge_graphs').download(f"/{self.project_name}/create_final_entities.parquet")
            self._entity_embedding_df = pd.read_parquet(entity_embedding_file)
        return self._entity_embedding_df

    @property
    def relationship_df(self):
        if self._relationship_df is None:
            relationship_file = self._supabase.storage.from_('knowledge_graphs').download(f"/{self.project_name}/create_final_relationships.parquet")
            self._relationship_df = pd.read_parquet(relationship_file)
        return self._relationship_df

    @property
    def report_df(self):
        if self._report_df is None:
            reports_file = self._supabase.storage.from_('knowledge_graphs').download(f"/{self.project_name}/create_final_community_reports.parquet")
            self._report_df = pd.read_parquet(reports_file)
        return self._report_df

    @property
    def text_unit_df(self):
        if self._text_unit_df is None:
            text_units_file = self._supabase.storage.from_('knowledge_graphs').download(f"/{self.project_name}/create_final_text_units.parquet")
            self._text_unit_df = pd.read_parquet(text_units_file)
        return self._text_unit_df