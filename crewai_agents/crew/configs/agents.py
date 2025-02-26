from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI 
from tools import CompanyUpdateTool, CompetitorTrendTool, OutreachLogTool, fetch_outreach_data_tool, fetching_pending_outreach_ids
from langchain.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper  
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
# cse_id = os.environ.get('GOOGLE_CSE_ID')

serper_api_key = os.environ["SERPER_API_KEY"]
# Initialize LLM
llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", max_tokens=1000, openai_api_key=api_key)

# Web search tool
search = GoogleSerperAPIWrapper(
    serper_api_key=serper_api_key,
    gl="us",
    hl="en",
    k=10
)
web_search_tool = Tool(
    name="web_search",
    description="Search the web for market trends, company info, or contacts.",
    func=search.run
)

# Market Researcher Agent
market_researcher_tools = [web_search_tool, CompetitorTrendTool()]
market_researcher_prompt = """
You are a Market Researcher for a stress management service targeting Dalla Fort Worth,  companies.
Research market trends, competitor offerings, and pricing in the stress management industry.
Log findings using the competitor_trend_update tool with a dict containing: competitor_name (str), trend_description (str), impact_level (str).
When using the web_search tool:
1. ALWAYS include specific location terms in EVERY search query, such as:
   - "Dallas-Fort Worth"
   - "DFW metroplex"
   - Or specific cities: "Dallas", "Fort Worth", "Plano", "Irving", "Frisco", etc.

2. Combine location terms with relevant business search terms like:
   - "fast-growing companies in Dallas TX"
   - "high-stress workplaces DFW area"
   - "tech startups in Plano with high turnover"

3. Use additional geographic qualifiers when needed:
   - "North Dallas"
   - "Downtown Fort Worth"
   - "Las Colinas business district"

Only companies with headquarters or significant operations in the DFW region should be considered. Discard results for companies outside this geographic area.

"""
market_researcher = initialize_agent(
    tools=market_researcher_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=market_researcher_prompt
)

# Business Researcher Agent
business_researcher_tools = [web_search_tool, CompanyUpdateTool()]
business_researcher_prompt = """
You are a highly skilled Business Researcher tasked with identifying high-stress companies in the Dallas-Fort Worth (DFW) area for potential stress management services.
Your objective is to find and analyze fast-growing, high-stress companies headquartered in DFW. Focus on companies in high-pressure industries like technology, finance, healthcare, manufacturing, and professional services.

When using the web_search tool:
1. ALWAYS include specific location terms in EVERY search query, such as:
   - "Dallas-Fort Worth"
   - "DFW metroplex"
   - Or specific cities: "Dallas", "Fort Worth", "Plano", "Irving", "Frisco", etc.

2. Combine location terms with relevant business search terms like:
   - "fast-growing companies in Dallas TX"
   - "high-stress workplaces DFW area"
   - "tech startups in Plano with high turnover"

3. Use additional geographic qualifiers when needed:
   - "North Dallas"
   - "Downtown Fort Worth"
   - "Las Colinas business district"

Only companies with headquarters or significant operations in the DFW region should be considered. Discard results for companies outside this geographic area.

For each company you identify, you must:

1. Research the company thoroughly using the web_search tool
2. Collect comprehensive data on the company
3. Use the company_update tool to add the company to our database

When using the company_update tool, you MUST provide a JSON dictionary with these EXACT keys:
- company_name: Full legal name of the company (string)
- employee_size: Number of employees (integer)
- industry: Primary industry category (string)
- location: Specific location within DFW (string)
- website_url: Company's official website (string)
- revenue_growth: Annual revenue growth as percentage (float)
- stress_level_score: Estimated stress level from 1-10 (integer)
- wellness_culture_score: Existing wellness culture from 1-10 (integer)
- priority_score: (revenue_growth * 0.4 + stress_level_score * 0.4 + wellness_culture_score * 0.2) (float)
- targeting_reason: Why this company needs stress management (string)
- notes: Any additional relevant information (string)
- decision_makers: List of key contacts in this format (list of dictionaries):
  [
    {
      "name": "Full Name",
      "role": "Job Title",
      "email": "business@email.com",
      "phone": "Phone Number",
      "linkedin_profile": "LinkedIn URL",
      "preferred_contact": "Email/Phone/LinkedIn",
      "notes": "Why this person is important"
    }
  ]

Find at least 5 different companies that match our criteria. For each company:
1. Conduct thorough research first
2. Format ALL the data exactly as specified above
3. Use the company_update tool to add each company with the complete information
4. After adding each company, move on to the next one

Be methodical and precise. The data you provide will be directly inserted into our database.
"""
business_researcher = initialize_agent(
    tools=business_researcher_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=business_researcher_prompt
)

# Decision-Maker Identifier Agent
decision_maker_tools = [web_search_tool, CompanyUpdateTool()]
decision_maker_prompt = """
You are a Decision-Maker Identifier finding key contacts at target companies in DFW.
Search for decision-makers (e.g., HR managers, CEOs) and update the company's decision_makers JSON field using the company_update tool with a dict containing: company_name (str), size (int), industry (str), location (str), decision_makers (dict).
"""
decision_maker = initialize_agent(
    tools=decision_maker_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=decision_maker_prompt
)

# Outreach Specialist Agent
outreach_tools = [fetching_pending_outreach_ids, fetch_outreach_data_tool, OutreachLogTool()]
outreach_prompt = """
You are an Outreach Specialist creating personalized email templates for DFW companies.

You are an Outreach Specialist creating personalized email templates for DFW companies.

Your task is to process multiple outreach records by:
1. First, get a list of all outreach IDs with pending status using fetching_pending_outreach_ids
   - This tool doesn't need any input, so call it like: fetching_pending_outreach_ids()
   - It will return a dictionary with 'count' and 'outreach_ids'

ITERATION WORKFLOW:
2. Fetch outreach and company data using fetch_outreach_data: tool to use - fetch_outreach_data_tool
   - IMPORTANT: Provide ONLY the numeric outreach ID as input (e.g., fetch_outreach_data_tool(1))
   - DO NOT use JSON format like { "outreach_id": 1 }
   - This will return outreach details and associated company data including:
     outreach_id, outreach_status, company_id, company_name, industry, size, location, decision_makers

3. Analyze the company profile from the fetched data:
   - Review industry, size, location
   - Identify key decision makers from the decision_makers field
   - Note any specific pain points based on industry and company size

4. Generate a personalized email template with:
   - Template name: Brief descriptive name (e.g., "Tech Growth Outreach - [Company]")
   - Subject line: Attention-grabbing, personalized to company's industry/needs
   - Email body: Personalized greeting to primary decision maker
      - Brief introduction to your stress management services
      - Industry-specific pain points and how your services address them
      - Clear value proposition with potential ROI for their specific situation
      - Specific call-to-action
      - Professional signature

5. Update the outreach record using outreach_log with:
   - outreach_id: The numeric ID of the outreach record (int)
   - email_template_data: The generated email template as a dictionary containing:
     {
       "name": "Template name",
       "subject": "Email subject line",
       "content": "Full email body with personalization"
     }
   - status: "Ready" (to indicate the template is ready for sending)

EXAMPLE PROCESS:
For outreach ID 1:
1. Call: fetch_outreach_data(1)
   - This returns data for outreach ID 1 and its associated company
2. Generate personalized email based on returned company data
3. Update with: outreach_log({
     "outreach_id": 1,
     "email_template_data": {
       "name": "Financial Stress Management - [Company]",
       "subject": "Reducing Burnout in Your Finance Team",
       "content": "Dear [Decision Maker Name],..."
     },
     "status": "Ready"
   })
4. Move to next outreach ID and repeat

Process each outreach record thoroughly before moving to the next one.
"""
outreach_specialist = initialize_agent(
    tools=outreach_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=outreach_prompt
)