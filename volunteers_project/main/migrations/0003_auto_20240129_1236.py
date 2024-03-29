# Generated by Django 3.2.23 on 2024-01-29 06:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20240127_1225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование региона')),
            ],
        ),
        migrations.RenameField(
            model_name='customuser',
            old_name='status',
            new_name='direction',
        ),
        migrations.AddField(
            model_name='customuser',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.region', verbose_name='Район'),
        ),
    ]
