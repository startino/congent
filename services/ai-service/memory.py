from supabase import create_client, Client
from typing import Optional, Dict, Any, Union
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AnyMessage
from langchain_core.messages.utils import message_to_dict, messages_from_dict
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from models.event import Event

# Initialize Supabase client
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"

class SupabaseChatMessageHistory(BaseChatMessageHistory):
    supabase: Client
    thread_id: str

    @property
    def messages(self):
        response = self.supabase.table('events').select('*').eq('profile_id', self.thread_id).execute()
        
        if response.get('error'):
            print(f"Error fetching events: {response['error']}")
            return {'chatMessageHistory': None, 'error': str(response['error'])}
        
        events: list[Event] = response['data']
        
        return messages_from_dict(events.message_object)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Insert new message into Supabase
        response = self.supabase.table('events').insert([
            {
                'content': message.content,
                'name': message.name,
                'profile_id': self.thread_id,
                'event_type': message.event_type,
                'message_object': message_to_dict(message)
            } for message in messages
        ]).execute()

        if response.get('error'):
            print('Error posting chat message: ', response['error'])
            return None

    def clear(self):
        response = self.supabase.table('events').delete().eq('profile_id', self.thread_id).execute()
        
        if response.get('error'):
            print(f"Error clearing events: {response['error']}")


    # # Parse events and add to chatMessageHistory
    # for event in events:
    #     ts_object = event.get('ts_object')
    #     if not ts_object:
    #         print('ts_object missing from event:', event)
    #         continue

    #     kwargs = ts_object.get('kwargs', {})

    #     if event['event_type'] in ['user', 'human']:
    #         chat_message_history.add_message(
    #             HumanMessage(
    #                 id=ts_object.get('id', 'HUMAN_MISSING_ID'),
    #                 name=event.get('name', 'HUMAN_MISSING_NAME'),
    #                 content=event['content']
    #             )
    #         )
    #     elif event['event_type'] == 'ai':
    #         chat_message_history.add_message(
    #             AIMessage(
    #                 name=event.get('name', 'AI_MISSING_NAME'),
    #                 content=event['content'],
    #                 tool_calls=kwargs.get('tool_calls')
    #             )
    #         )
    #     elif event['event_type'] == 'tool':
    #         chat_message_history.add_message(
    #             ToolMessage(
    #                 name=event.get('name', 'TOOL_MISSING_NAME'),
    #                 content=event['content'],
    #                 tool_call_id=kwargs.get('tool_call_id')
    #             )
    #         )
    #     else:
    #         print(f"Unknown event type: {event['event_type']}")