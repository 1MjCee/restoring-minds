from crewai import Task
from .agents import get_agents

def get_tasks():
    """Load tasks from the database and return a list of CrewAI Task objects."""
    from django.apps import apps
    TaskModel = apps.get_model('crewai_agents', 'Task')

    tasks = []
    agents = {agent.role: agent for agent in get_agents()}
    for django_task in TaskModel.objects.all():
        assigned_agent = None
        if django_task.assigned_agent:
            assigned_agent = agents.get(django_task.assigned_agent.role)

        task = Task(
            description=django_task.description,
            expected_output=django_task.expected_output,
            agent=assigned_agent
        )
        tasks.append(task)
    return tasks