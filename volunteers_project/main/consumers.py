import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Task, UserTask, CustomUser
from django.db.models import Q


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'task_group'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):
        # Удаление из группы при отключении клиента
        await self.channel_layer.group_discard(
            'task_group',
            self.channel_name
        )


    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            telegram_user_id = data.get('user')
            task_id = data.get('task_id')

            if telegram_user_id and task_id:
                user = await database_sync_to_async(CustomUser.objects.get)(
                    telegram_user_id=telegram_user_id,
                )

                task = await database_sync_to_async(Task.objects.get)(
                    pk=task_id,
                )

                user_task = await database_sync_to_async(UserTask.objects.create)(
                    user=user,
                    task=task,
                    status='на выполнении'
                )

                updated_task = await self.update_task_by_pk(task_id)

                response_data = {
                    'type': 'send_message',
                    'action': 'user_task_created',
                    'user_task_id': user_task.id,
                    'user': telegram_user_id,
                    'task_id': task_id,
                }

                await self.channel_layer.group_send(self.room_group_name, response_data)
        except json.JSONDecodeError:
            print("Invalid JSON format")


    def __serialize_task(self, task):
        return {
            'task_id': task.pk,
            'task_name': task.name,
            'text': task.text,
            'score': task.score,
            'start_date': task.start_date.isoformat(),
            'end_date': task.end_date.isoformat(),
        }


    @database_sync_to_async
    def update_task_by_pk(self, task_id):
        try:
            task = Task.objects.get(pk=task_id)
            task.assigned = True
            task.save()
            return task
        except Task.DoesNotExist:
            return None


    @database_sync_to_async
    def get_user_ids(self):
        user_ids_queryset = CustomUser.objects.filter(
            ~Q(telegram_user_id='') & ~Q(telegram_user_id__isnull=True)
        )

        user_ids = list(user_ids_queryset.values_list('telegram_user_id', flat=True))

        return user_ids


    async def task_status_create(self, event):
        task = event.get("task")

        user_ids = user_ids = await self.get_user_ids()

        response_data = {
            'type': 'send_message',
            'action': 'task_status_create',
            'task': self.__serialize_task(task),
            'users': user_ids
        }

        await self.channel_layer.group_send(self.room_group_name, response_data)


    async def send_message(self, res):
        """ Receive message from room group """
        await self.send(text_data=json.dumps({
            "payload": res,
        }))
