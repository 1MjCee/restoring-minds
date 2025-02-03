from django.apps import AppConfig


class CrewaiAgentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crewai_agents'

    def ready(self):
        import crewai_agents.signals.outreach
