from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task


@receiver(post_save, sender=Task)
def send_payment_status_update(sender, instance, **kwargs):
    pass
    # if instance.assigned == False:
    #     channel_layer = get_channel_layer()
    #     async_to_sync(channel_layer.group_send)(
    #         'task_group',
    #         {
    #             'type': 'task_status_create',
    #             'task': instance,
    #         }
    #     )
