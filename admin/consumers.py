from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
import json
from channels.db import database_sync_to_async
from inservice.models import Thread, ChatMessage


User = get_user_model()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope['user']
        chat_room = f'user_chatroom_{user.id}'
        print('chat room: ', chat_room)
        self.chat_room = chat_room
        await self.channel_layer.group_add(
            chat_room,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        received_data = json.loads(event['text'])
        msg = received_data.get('message')
        print('msg::: ', msg)
        send_by_id = received_data.get('send_by')
        send_to_id = received_data.get('send_to')
        thread_id = received_data.get('thread_id')
        if not msg:
            return False
        
        send_by_user = await self.get_user_object(send_by_id)
        send_to_user = await self.get_user_object(send_to_id)
        thread_obj = await self.get_thread(thread_id)
        if not send_by_user:
            print('Error:: sent by user is incorrect')
        if not send_to_user:
            print('Error:: send to user is incorrect')
        if not thread_obj:
            print('Error:: Thread id is incorrect')
        await self.create_chatmessage(thread_obj, send_by_user, msg)
        unseen_count = await self.get_unseen_messages_count(self.scope['user'], thread_obj)
        print('unseen_count: ', unseen_count)
        other_user_chat_room = f'user_chatroom_{send_to_id}'
        self_user = self.scope['user']
        response = {
            'message': msg,
            'send_by': self_user.id,
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('disconnected: ', event)
        await self.send({
            "type": "websocket.send",
            # "text": event["text"],
        })

    async def chat_message(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event['text']
        })

    @database_sync_to_async
    def get_user_object(self, user_id):
        print("user_id",user_id)
        qs = User.objects.filter(id=user_id)
        
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        print("thread_id",thread_id)
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj
    
    @database_sync_to_async
    def create_chatmessage(self, thread, user, msg):
        ChatMessage.objects.create(thread=thread, user=user, message=msg)

    @database_sync_to_async
    def get_unseen_messages_count(self, user, thread):
        """
        Get the count of unseen messages for a particular user in a thread.
        """
        return thread.chatmessage_thread.filter(user__in=[thread.first_person, thread.second_person], is_seen=False).exclude(user=user).count()
    