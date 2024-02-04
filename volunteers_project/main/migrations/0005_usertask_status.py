# Generated by Django 3.2.23 on 2024-02-04 04:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20240201_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertask',
            name='status',
            field=models.CharField(choices=[('выполнено', 'Выполнено'), ('на выполнении', 'На выполнении'), ('не выполнено', 'Не выполнено')], default='на выполнении', max_length=20, verbose_name='Статус'),
        ),
    ]
