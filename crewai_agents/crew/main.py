import os
import django
import sys
from crew import get_crew

"""Calcuate the path to the project root directory."""
current_dir = os.path.dirname(os.path.abspath(__file__))  
project_root = os.path.abspath(os.path.join(current_dir, '../../')) 

"""add the project root to sys.path"""
if project_root not in sys.path:
    sys.path.append(project_root)

"""Set up Django environment"""
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restoring_minds.settings')
django.setup()

"""Run the crew"""
def main():
    crew = get_crew("Prospect AI Crew")

    # Run the crew
    result = crew.kickoff()
    print("Crew Execution Result:")
    print(result)

if __name__ == "__main__":
    main()