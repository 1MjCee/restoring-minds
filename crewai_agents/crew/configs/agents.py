from crewai import Agent
from tools import llm, serper_dev_tool, get_companies_data, populate_companies, populate_contact_persons

def get_agents():
    """Load agents from the database and return a list of CrewAI Agent objects."""
    from django.apps import apps
    AgentModel = apps.get_model('crewai_agents', 'Agent')

    agents = []
    for django_agent in AgentModel.objects.all():
        if not django_agent.role or not django_agent.goal or not django_agent.backstory:
            raise ValueError(f"Agent with ID {django_agent.id} is missing required fields (role, goal, or backstory).")

        # Load tools associated with the agent
        tools = []
        for tool in django_agent.tools.all():
            if tool.name == 'SerperDevTool':
                tools.append(serper_dev_tool)
            if tool.name == 'PopulateCompanyData':
                tools.append(populate_companies)
            if tool.name == 'PopulateContactPersons':
                tools.append(populate_contact_persons)
            if tool.name == 'GetCompanyData':
                tools.append(get_companies_data)


        agent = Agent(
            role=django_agent.role,
            goal=django_agent.goal,
            backstory=django_agent.backstory,
            tools=tools,
            verbose=django_agent.verbose,
            memory=django_agent.memory,
            llm=llm
        )
        agents.append(agent)
    return agents