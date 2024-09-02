from pydantic import BaseModel
from langchain_core.messages import AnyMessage

class Event(BaseModel):
    """
    Should be identical to `events` table in Supabase.
    """
    id: str
    session_id: str
    created_at: str
    content: str | None
    event_type: str | None
    name: str | None
    sources: str | None
    message_object: dict