from crewai_agents.crew.configs.agents import market_researcher, business_researcher, decision_maker, outreach_specialist

def run_manually(agent_name, input_data):
    """Run an agent manually and print the result."""
    agents = {
        "market_researcher": market_researcher,
        "business_researcher": business_researcher,
        "decision_maker": decision_maker,
        "outreach_specialist": outreach_specialist
    }
    agent = agents.get(agent_name)
    if not agent:
        print(f"Unknown agent: {agent_name}")
        return

    print(f"Running {agent_name} manually...")
    result = agent.run(input_data)
    print(f"Result: {result}")

def schedule_tasks():
    """Setup for scheduled tasks is handled in settings.py with Celery Beat."""
    print("Scheduled tasks are configured in settings.py with Celery Beat.")
    print("Run 'celery -A myproject beat' to start the scheduler alongside the worker.")