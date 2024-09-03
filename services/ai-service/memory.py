import json
from uuid import UUID
from supabase import Client
from typing import Any, Sequence, Union
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage, BaseMessage, message_to_dict
from langchain_core.messages.utils import messages_from_dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from models.event import Event

class SupabaseChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, supabase: Client, session_id: UUID):
        self.supabase = supabase
        
        # Convert UUID to string to make it JSON serializable
        self.session_id: str = str(session_id)

    @property
    def messages(self):
        response = self.supabase.table('events').select('*').eq('session_id', self.session_id).execute()
        
        if not response.data:
            print('Error getting chat messages')
            return []
        
        events: list[Event] = [Event(**event) for event in response.data]

        return messages_from_dict([event.message_object for event in events])

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
                
        # Insert new message into Supabase        
        response = self.supabase.table('events').insert([
            {
                'content': message.content,
                'name': message.name,
                'session_id': self.session_id,
                'event_type': message.type,
                'message_object': message_to_dict(message)
            } for message in messages
        ]).execute()

        if not response.data:
            print('Error posting chat message')
            

    def clear(self):
        response = self.supabase.table('events').delete().eq('session_id', self.session_id).execute()
        
        if not response.data:
            print('Error clearing chat messages')
