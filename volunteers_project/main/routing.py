from django.urls import re_path
from .consumers import TaskConsumer


websocket_urlpatterns = [
    re_path('task_updates/', TaskConsumer.as_asgi()),
    # re_path(r'ws/payment/$', TaskConsumer.as_asgi()),
]
