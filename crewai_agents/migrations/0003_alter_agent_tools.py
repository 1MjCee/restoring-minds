# Generated by Django 5.1.5 on 2025-01-22 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0002_tool_remove_agent_tools_agent_tools'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agent',
            name='tools',
            field=models.ManyToManyField(related_name='agents', to='crewai_agents.tool'),
        ),
    ]
