"""
prospecting_agents.py - Specialized agents for the Prospecting AI Team

This module implements the specialized agents needed for identifying and approaching
fast-growing, high-stress companies in the DFW area for stress management services.
"""

from agents import LLMAgent, MultiAgentSystem
from tools import SearchTool, WebBrowserTool, MemoryTool

# Common tools that will be used by multiple agents
def create_common_tools():
    """Create the common tools used by the prospecting agents."""
    return {
        "search": SearchTool(
            name="WebSearch",
            description="Search for company information, industry data, and market trends",
            search_provider="google",
            max_results=10,
            rate_limit=20,
        ),
        
        "browser": WebBrowserTool(
            name="WebBrowser",
            description="Browse company websites, LinkedIn pages, and industry reports",
            user_agent="Prospecting Assistant Browser/1.0",
            timeout=45,
            max_pages=10,
        ),
        
        "memory": MemoryTool(
            name="ProspectingMemory",
            description="Store and retrieve information about companies, contacts, and market data",
            storage_limit=5000,
        ),
    }


def create_market_researcher_agent() -> LLMAgent:
    """
    Create the Market Researcher agent for identifying and analyzing market needs
    and opportunities for stress management training.
    """
    # Get common tools
    common_tools = create_common_tools()
    
    # Create a custom system prompt for the Market Researcher
    system_prompt = """You are a Market Researcher specializing in the stress management and emotional intelligence training market.
    
Your primary focus is on fast-growing and high-stress companies in the Dallas-Fort Worth (DFW) area.

Your responsibilities include:
1. Identifying common challenges and pain points among fast-growing and high-stress companies
2. Staying updated on industry trends, competitors, and demand for stress management training
3. Researching standard fees for stress management workshops in the DFW area
4. Suggesting competitive fee ranges to position offerings effectively
5. Identifying success metrics and compiling reports on the financial impact of stress on businesses

Always provide data-backed insights and specific recommendations for the DFW market.
When researching, always prioritize the most recent information available.
"""

    # Create the Market Researcher agent
    return LLMAgent(
        name="Market Researcher",
        description="Identifies and analyzes market needs and opportunities for stress management training in fast-growing, high-stress companies in DFW",
        tools=[
            common_tools["search"],
            common_tools["browser"],
            common_tools["memory"],
        ],
        memory_size=30,  # Remember more context for market research
        model_name="gpt-4",
        temperature=0.3,  # Lower temperature for more factual, research-oriented outputs
        system_prompt=system_prompt,
    )


def create_business_research_agent() -> LLMAgent:
    """
    Create the Business Research and Identification agent for identifying
    and qualifying potential target companies.
    """
    # Get common tools
    common_tools = create_common_tools()
    
    # Create a custom system prompt for the Business Research agent
    system_prompt = """You are a Business Research and Identification specialist focusing on prospecting for stress management services.

Your primary focus is identifying fast-growing and high-stress companies headquartered in the Dallas-Fort Worth (DFW) area.

Your responsibilities include:
1. Searching for companies with headquarters in DFW experiencing rapid growth and increased revenue
2. Identifying companies prone to high stress (acquisition companies, manufacturing, technology, finance)
3. Scoring companies to prioritize those likely to procure stress-management services
4. Providing tailored recommendations for approaching each business with estimated ROI
5. Creating a database of target companies with relevant details (leadership team size, employee count, industry, location)

When evaluating companies, use these criteria:
- Growth rate (higher is better)
- Industry stress level (higher means more need)
- Company size (50+ employees ideal)
- Existing wellness initiatives (some investment but room for growth is ideal)
- Recent changes (mergers, acquisitions, leadership changes)

Always prioritize companies based on a combined score of these factors.
"""

    # Create the Business Research agent
    return LLMAgent(
        name="Business Research Agent",
        description="Identifies and qualifies potential target companies for prospecting and lead generation in the DFW area",
        tools=[
            common_tools["search"],
            common_tools["browser"],
            common_tools["memory"],
        ],
        memory_size=40,  # Remember more context for company research
        model_name="gpt-4",
        temperature=0.2,  # Low temperature for precise, analytical research
        system_prompt=system_prompt,
    )


def create_decision_maker_agent() -> LLMAgent:
    """
    Create the Decision-Maker Identifier agent for identifying and gathering
    contact information for key decision-makers within target companies.
    """
    # Get common tools
    common_tools = create_common_tools()
    
    # Create a custom system prompt for the Decision-Maker Identifier
    system_prompt = """You are a Decision-Maker Identifier specializing in identifying key contacts for stress management training services.

Your primary focus is finding the right decision-makers in fast-growing and high-stress companies in the Dallas-Fort Worth (DFW) area.

Your responsibilities include:
1. Using Google, LinkedIn, and other platforms to identify HR leads, training managers, or executive decision-makers
2. Gathering names, roles, and contact information for these individuals
3. Using publicly available data to find email addresses and phone numbers
4. Creating a database of decision-makers for outreach purposes

When identifying decision-makers, prioritize:
- HR Directors/VPs
- Chief People Officers
- Training & Development Managers
- Wellness Program Directors
- C-suite executives (particularly in smaller companies)

Always verify information using multiple sources when possible and format contact information consistently.
Remember to only use publicly available information and respect privacy guidelines.
"""

    # Create the Decision-Maker Identifier agent
    return LLMAgent(
        name="Decision-Maker Identifier",
        description="Identifies and gathers contact information for key decision-makers within target companies in DFW",
        tools=[
            common_tools["search"],
            common_tools["browser"],
            common_tools["memory"],
        ],
        memory_size=30,
        model_name="gpt-4",
        temperature=0.3,
        system_prompt=system_prompt,
    )


def create_outreach_specialist_agent() -> LLMAgent:
    """
    Create the Outreach Specialist agent for supporting outreach efforts
    with tailored communication materials.
    """
    # Get common tools
    common_tools = create_common_tools()
    
    # Create a custom system prompt for the Outreach Specialist
    system_prompt = """You are an Outreach Specialist focusing on stress management training services.

Your primary focus is creating personalized outreach materials for decision-makers in fast-growing and high-stress companies in the Dallas-Fort Worth (DFW) area.

Your responsibilities include:
1. Developing personalized email templates and LinkedIn message scripts tailored to each target's needs
2. Identifying the most promising leads and prioritizing them for outreach
3. Providing detailed lists of decision-makers with their preferred communication methods
4. Creating real-time alerts for newly identified high-stress companies, competitor changes, and industry trends

When creating outreach materials:
- Personalize based on company pain points (rapid growth, recent merger, industry-specific stressors)
- Focus on ROI and business impact rather than just wellness benefits
- Keep emails concise (3-5 short paragraphs maximum)
- Include a clear call to action
- Use a professional but conversational tone

Your communications should always emphasize how stress management directly impacts business performance metrics like retention, productivity, and innovation.
"""

    # Create the Outreach Specialist agent
    return LLMAgent(
        name="Outreach Specialist",
        description="Creates tailored communication materials and provides detailed contact strategies for decision-makers",
        tools=[
            common_tools["search"],
            common_tools["browser"],
            common_tools["memory"],
        ],
        memory_size=35,
        model_name="gpt-4",
        temperature=0.7,  # Higher temperature for more creative outreach materials
        system_prompt=system_prompt,
    )


def create_prospecting_ai_team() -> MultiAgentSystem:
    """
    Create the complete Prospecting AI Team as a multi-agent system.
    """
    # Create all the specialized agents
    market_researcher = create_market_researcher_agent()
    business_researcher = create_business_research_agent()
    decision_maker_identifier = create_decision_maker_agent()
    outreach_specialist = create_outreach_specialist_agent()
    
    # Create the multi-agent system
    return MultiAgentSystem(
        name="Prospecting AI Team",
        description="A team of specialized agents for identifying and approaching fast-growing, high-stress companies in the DFW area for stress management services",
        agents=[
            market_researcher,
            business_researcher,
            decision_maker_identifier,
            outreach_specialist,
        ],
    )


# Example of using the Prospecting AI Team
if __name__ == "__main__":
    # Create the Prospecting AI Team
    prospecting_team = create_prospecting_ai_team()
    
    # Example queries for each agent
    market_research_query = "What are the current market rates for corporate stress management workshops in the DFW area, and what ROI metrics are most convincing to potential clients?"
    
    business_research_query = "Identify the top 5 fastest-growing technology companies in DFW that would benefit from stress management training, including their growth rates and employee counts."
    
    decision_maker_query = "For Bottle Rocket Studios in Addison, TX, who are the key decision-makers for implementing wellness or training programs?"
    
    outreach_query = "Create a personalized email template for the HR Director of a fast-growing fintech company that's recently undergone a merger, emphasizing how stress management training can help with the transition."
    
    # Process each query with the appropriate agent
    # In a real implementation, the router would handle this automatically
    for agent in prospecting_team.agents:
        if agent.name == "Market Researcher":
            response = agent.run(market_research_query)
            print(f"\n{agent.name} Response:\n{response}\n")
            
        elif agent.name == "Business Research Agent":
            response = agent.run(business_research_query)
            print(f"\n{agent.name} Response:\n{response}\n")
            
        elif agent.name == "Decision-Maker Identifier":
            response = agent.run(decision_maker_query)
            print(f"\n{agent.name} Response:\n{response}\n")
            
        elif agent.name == "Outreach Specialist":
            response = agent.run(outreach_query)
            print(f"\n{agent.name} Response:\n{response}\n")