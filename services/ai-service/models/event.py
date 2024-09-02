from pydantic import BaseModel
from pydantic import BaseModel


class Event(BaseModel):
    """
    Should be identical to `events` table in Supabase.
    """
    id: str
    created_at: str
    content: str
    event_type: str
    name: str
    profile_id: str
    message_object: str