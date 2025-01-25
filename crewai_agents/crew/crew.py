from crewai import Crew, Process
from configs.agents import get_agents
from configs.tasks import get_tasks

def get_crew(crew_name):
    """Load a crew from the database and return a CrewAI Crew object."""
    from django.apps import apps
    CrewModel = apps.get_model('crewai_agents', 'Crew')

    django_crew = CrewModel.objects.get(name=crew_name)
    agents = get_agents()
    tasks = get_tasks()

    return Crew(
        agents=agents,
        tasks=tasks,
        process=getattr(Process, django_crew.process),
        verbose=django_crew.verbose
    )