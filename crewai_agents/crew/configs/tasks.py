from celery import shared_task
from .agents import market_researcher, business_researcher, decision_maker, outreach_specialist
from django.apps import apps
from django.utils import timezone

@shared_task(bind=True, max_retries=3)
def run_agent_task(self, task_id, agent_name, input_data):
    try:
        AgentTask = apps.get_model('crewai_agents', 'AgentTask')
        task = AgentTask.objects.get(id=task_id)
        task.status = "RUNNING"
        task.started_at = timezone.now()
        task.save()

        agents = {
            "market_researcher": market_researcher,
            "business_researcher": business_researcher,
            "decision_maker": decision_maker,
            "outreach_specialist": outreach_specialist
        }
        agent = agents.get(agent_name)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_name}")

        result = agent.run(input_data)

        task.status = "COMPLETED"
        task.completed_at = timezone.now()
        task.result = result
        task.save()

        AgentLog = apps.get_model('crewai_agents', 'AgentLog')
        AgentLog.objects.create(task=task, output=result)
        return result

    except Exception as e:
        task.status = "FAILED"
        task.error_message = str(e)
        task.save()
        raise self.retry(exc=e, countdown=60) 

# Specific tasks for scheduling
@shared_task
def run_market_researcher_scheduled():
    AgentTask = apps.get_model('crewai_agents', 'AgentTask')
    task = AgentTask.objects.create(
        agent_name="market_researcher",
        input_data="Analyze stress management trends in DFW",
        status="PENDING"
    )
    return run_agent_task(task.id, "market_researcher", task.input_data)

@shared_task
def run_business_researcher_scheduled():
    AgentTask = apps.get_model('crewai_agents', 'AgentTask')
    task = AgentTask.objects.create(
        agent_name="business_researcher",
        input_data="Find high-stress tech companies in DFW",
        status="PENDING"
    )
    return run_agent_task(task.id, "business_researcher", task.input_data)

@shared_task
def run_decision_maker_scheduled():
    AgentTask = apps.get_model('crewai_agents', 'AgentTask')
    task = AgentTask.objects.create(
        agent_name="decision_maker",
        input_data="Find decision-makers for a tech company in DFW",
        status="PENDING"
    )
    return run_agent_task(task.id, "decision_maker", task.input_data)

@shared_task
def run_outreach_specialist_scheduled():
    AgentTask = apps.get_model('crewai_agents', 'AgentTask')
    task = AgentTask.objects.create(
        agent_name="outreach_specialist",
        input_data="Plan outreach for a tech company in DFW",
        status="PENDING"
    )
    return run_agent_task(task.id, "outreach_specialist", task.input_data)