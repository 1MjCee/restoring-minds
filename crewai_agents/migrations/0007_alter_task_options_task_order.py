# Generated by Django 5.1.5 on 2025-01-26 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0006_task_context_workflowstep'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='task',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
