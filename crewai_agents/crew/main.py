import os
import sys
import django
from configs import market_researcher, business_researcher, outreach_specialist, run_business_researcher_scheduled, decision_maker

"""Calculate the path to the project root directory."""
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))

"""Add the project root to sys.path"""
if project_root not in sys.path:
    sys.path.append(project_root)

"""Set up Django environment"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restoring_minds.settings')
django.setup()

def run(agent_name=None, input_data=None):
    """Run a single agent or all agents manually and print the results."""
    agents = {
        "market_researcher": market_researcher, 
        "business_researcher": business_researcher,
        "decision_maker": decision_maker,
        "outreach_specialist": outreach_specialist
    }

    # Define specific inputs for each agent based on their tasks
    agent_tasks = {
        "market_researcher": "Research and log market trends, competitor offerings, and pricing in the stress management industry for Dallas-Fort Worth companies.",
        "business_researcher": "Identify and add 5 high-stress companies in the Dallas-Fort Worth area to the database.",
        "decision_maker": "Find and update decision-makers for all companies in the Dallas-Fort Worth area without decision-makers in the database.",
        "outreach_specialist": "Process all pending outreach records by generating personalized email templates for DFW companies."
    }

    if agent_name:
        print(f"Running {agent_name} manually...")
        agent = agents.get(agent_name)
        if agent:
            task = agent_tasks.get(agent_name, f"Perform your task for {agent_name}")
            result = agent.run(task)
            print(f"{agent_name} Result: {result}")
    else:
        print("Running all agents manually...")
        for name, agent in agents.items():
            print(f"Running {name}...")
            # Use the specific task description for each agent
            task = agent_tasks.get(name, f"Perform your task for {name}")
            result = agent.run(task)
            print(f"{name} Result: {result}")

if __name__ == "__main__":
    run() 
    