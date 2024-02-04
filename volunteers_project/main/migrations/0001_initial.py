# Generated by Django 3.2.23 on 2024-01-27 06:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone_number', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=12, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=12, null=True, verbose_name='Фамилия')),
                ('is_active', models.BooleanField(default=True, verbose_name='Прошел активацию')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Служебный аккаунт')),
                ('status', models.CharField(choices=[('нарко', 'нарко'), ('экологическое', 'экологическое'), ('культурное', 'культурное'), ('спортивное', 'спортивное')], max_length=20, verbose_name='Направление')),
                ('telegram_user_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='Телеграм ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
        ),
        migrations.CreateModel(
            name='UserWork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(verbose_name='Ссылка')),
                ('status', models.CharField(choices=[('подтверждено', 'Подтверждено'), ('не подтверждено', 'Не подтверждено')], max_length=20, verbose_name='Статус')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Работа пользователя',
                'verbose_name_plural': 'Работы пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.PositiveIntegerField(verbose_name='Балл')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Балл пользователя',
                'verbose_name_plural': 'Баллы пользователей',
            },
        ),
    ]
