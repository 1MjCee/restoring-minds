# Generated by Django 5.1.5 on 2025-01-23 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0003_alter_agent_tools'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tool',
            name='config',
        ),
        migrations.AddField(
            model_name='tool',
            name='description',
            field=models.TextField(default=''),
        ),
    ]
