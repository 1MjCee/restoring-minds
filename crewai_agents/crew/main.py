import os
import sys
import django
from configs import market_researcher, business_researcher, outreach_specialist, run_business_researcher_scheduled

"""Calculate the path to the project root directory."""
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))

"""Add the project root to sys.path"""
if project_root not in sys.path:
    sys.path.append(project_root)

"""Set up Django environment"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restoring_minds.settings')
django.setup()

def run_manually(agent_name=None, input_data=None):
    """Run a single agent or all agents manually and print the results."""
    agents = {
        # "market_researcher": market_researcher,
        "business_researcher": run_business_researcher_scheduled,
        "outreach_specialist": outreach_specialist
    }

    print("Running all agents manually...")
    for name, agent in agents.items():
        print(f"Running {name}...")
        result = agent.run(f"Perform your task for {name}")
        print(f"{name} Result: {result}")

if __name__ == "__main__":
    run_manually() 
    