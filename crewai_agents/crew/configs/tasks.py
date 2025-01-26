from crewai import Task
from .agents import get_agents

def get_tasks():
    """Load tasks from the database and return a list of CrewAI Task objects."""
    from django.apps import apps
    TaskModel = apps.get_model('crewai_agents', 'Task')

    tasks = []
    agents = {agent.role: agent for agent in get_agents()}
    for django_task in TaskModel.objects.all().order_by('order'):
        assigned_agent = None
        if django_task.assigned_agent:
            assigned_agent = agents.get(django_task.assigned_agent.role)
        
        # Get the names of tasks in the context field
        context_tasks = django_task.context.all()

         # Create a list of fully initialized Task objects for the context parameter
        crewai_context = [
            Task(
                description=t.description,
                expected_output=t.expected_output,
                agent=agents.get(t.assigned_agent.role) if t.assigned_agent else None,
                config={}
            )
            for t in context_tasks
        ]

        task = Task(
            description=django_task.description,
            expected_output=django_task.expected_output,
            agent=assigned_agent,
            context=crewai_context,
            config={}
        )
        tasks.append(task)
    return tasks