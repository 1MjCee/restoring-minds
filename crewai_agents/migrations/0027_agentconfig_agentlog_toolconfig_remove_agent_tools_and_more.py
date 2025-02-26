# Generated by Django 5.1.6 on 2025-02-26 03:41

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crewai_agents', '0026_remove_task_callback_remove_task_output_json'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('agent_type', models.CharField(choices=[('market_researcher', 'Market Researcher'), ('business_researcher', 'Business Researcher'), ('decision_maker_identifier', 'Decision Maker Identifier'), ('outreach_specialist', 'Outreach Specialist')], max_length=50)),
                ('description', models.TextField()),
                ('model_name', models.CharField(default='gpt-4', max_length=50)),
                ('temperature', models.FloatField(default=0.5)),
                ('system_prompt', models.TextField()),
                ('tools', models.JSONField(default=list, help_text='List of tool names this agent can use')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Agent Configuration',
                'verbose_name_plural': 'Agent Configurations',
            },
        ),
        migrations.CreateModel(
            name='AgentLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('agent_name', models.CharField(max_length=100)),
                ('input_text', models.TextField()),
                ('output_text', models.TextField(blank=True, null=True)),
                ('intermediate_steps', models.JSONField(blank=True, default=list, null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('STARTED', 'Started'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')], default='STARTED', max_length=20)),
                ('execution_time', models.FloatField(blank=True, help_text='Execution time in seconds', null=True)),
                ('token_usage', models.JSONField(blank=True, default=dict, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Agent Log',
                'verbose_name_plural': 'Agent Logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ToolConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('tool_type', models.CharField(choices=[('database', 'Database Tool'), ('search', 'Search Tool'), ('browser', 'Browser Tool'), ('email', 'Email Tool'), ('analysis', 'Analysis Tool'), ('memory', 'Memory Tool')], max_length=50)),
                ('description', models.TextField()),
                ('configuration', models.JSONField(default=dict, help_text='Configuration parameters for the tool')),
                ('rate_limit', models.IntegerField(default=0, help_text='Rate limit in requests per minute (0 for unlimited)')),
                ('requires_auth', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Tool Configuration',
                'verbose_name_plural': 'Tool Configurations',
            },
        ),
        migrations.RemoveField(
            model_name='agent',
            name='tools',
        ),
        migrations.RemoveField(
            model_name='crew',
            name='agents',
        ),
        migrations.RemoveField(
            model_name='task',
            name='assigned_agent',
        ),
        migrations.RemoveField(
            model_name='contactperson',
            name='company',
        ),
        migrations.RemoveField(
            model_name='crew',
            name='tasks',
        ),
        migrations.RemoveField(
            model_name='task',
            name='context',
        ),
        migrations.CreateModel(
            name='AgentTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agent_type', models.CharField(max_length=50)),
                ('input_text', models.TextField()),
                ('context_data', models.JSONField(blank=True, default=dict, null=True)),
                ('result_data', models.JSONField(blank=True, default=dict, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RUNNING', 'Running'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('celery_task_id', models.CharField(blank=True, max_length=50, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='agent_tasks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Agent Task',
                'verbose_name_plural': 'Agent Tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ToolLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tool_name', models.CharField(max_length=100)),
                ('called_at', models.DateTimeField(auto_now_add=True)),
                ('input_data', models.JSONField(blank=True, default=dict, null=True)),
                ('output_data', models.JSONField(blank=True, default=dict, null=True)),
                ('execution_time', models.FloatField(blank=True, help_text='Execution time in seconds', null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('agent_log', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tool_logs', to='crewai_agents.agentlog')),
            ],
            options={
                'verbose_name': 'Tool Log',
                'verbose_name_plural': 'Tool Logs',
                'ordering': ['-called_at'],
            },
        ),
        migrations.DeleteModel(
            name='Tool',
        ),
        migrations.DeleteModel(
            name='Agent',
        ),
        migrations.DeleteModel(
            name='ContactPerson',
        ),
        migrations.DeleteModel(
            name='Crew',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
