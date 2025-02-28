from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI 
from tools import (CompanyUpdateTool, CompetitorTrendTool, OutreachLogTool, fetch_outreach_data_tool,
                   fetching_pending_outreach_ids, fetch_companies_tool, update_decision_makers_tool
                   )
from langchain.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper  
from langchain_community.utilities import GoogleSerperAPIWrapper
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
serper_api_key = os.environ["SERPER_API_KEY"]
llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", max_tokens=4000, openai_api_key=api_key)

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
    prompt=market_researcher_prompt,
    max_iterations=100,
)

# Business Researcher Agent
business_researcher_tools = [web_search_tool, CompanyUpdateTool()]
business_researcher_prompt = """
You are a highly skilled Business Researcher tasked with identifying and adding high-stress companies in the Dallas-Fort Worth (DFW) area to a database for potential stress management services. Your objective is to find and analyze fast-growing, high-stress companies headquartered in DFW, focusing on high-pressure industries like technology, finance, healthcare, manufacturing, and professional services.

This is NOT a generic research task about the role of a business researcher. Instead, follow these EXACT steps for each company:

1. Use the web_search tool to research fast-growing, high-stress companies in DFW:
   - ALWAYS include specific location terms in EVERY search query, such as:
     - "Dallas-Fort Worth"
     - "DFW metroplex"
     - Or specific cities: "Dallas", "Fort Worth", "Plano", "Irving", "Frisco", etc.
   - Combine location terms with relevant business search terms like:
     - "fast-growing companies in Dallas TX"
     - "high-stress workplaces DFW area"
     - "tech startups in Plano with high turnover"
   - Use additional geographic qualifiers when needed:
     - "North Dallas"
     - "Downtown Fort Worth"
     - "Las Colinas business district"
   - Only consider companies with headquarters or significant operations in the DFW region. Discard results for companies outside this area.

2. For each company identified:
   - Conduct thorough research using web_search to collect comprehensive data.
   - Gather ALL the following required fields:
     - company_name: Full legal name (string)
     - employee_size: Number of employees (integer)
     - industry: Primary industry category (string)
     - location: Specific location within DFW (string)
     - website_url: Official website (string)
     - revenue_growth: Annual revenue growth as percentage (float)
     - stress_level_score: Estimated stress level from 1-10 (integer)
     - wellness_culture_score: Existing wellness culture from 1-10 (integer)
     - priority_score: Calculate as (revenue_growth * 0.4 + stress_level_score * 0.4 + wellness_culture_score * 0.2) (float)
     - targeting_reason: Why this company needs stress management (string)
     - notes: Additional relevant information (string)
     - decision_makers: Leave empty (set as an empty list: [])

3. Use the company_update tool to add each company to the database:
   - Format the data as a JSON dictionary with ALL the exact keys listed above.
   - Call company_update with the JSON dictionary for each company.
   - Process one company fully (research and update) before moving to the next.

Your task is to identify and add at least 5 different companies that match these criteria. Do NOT stop until you have successfully added 5 companies to the database using company_update. Be methodical and precise. The data you provide will be directly inserted into our database.

Start by searching for candidate companies NOW. Do not research unrelated topics like the role of a business researcher.
"""
business_researcher = initialize_agent(
    tools=business_researcher_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=business_researcher_prompt,
    max_iterations=100,
)

# Decision-Maker Identifier Agent
decision_maker_tools = [fetch_companies_tool, web_search_tool, update_decision_makers_tool]
decision_maker_prompt = """
You are a Decision-Maker Identifier tasked with finding key contacts (e.g., HR managers, CEOs) at target companies in the Dallas-Fort Worth (DFW) area and updating their decision_makers field in the database.
Follow these EXACT steps for each company to ensure correct JSON output:

1. Call fetch_companies_tool (ignore any input) to get a list of companies with no decision-makers. Output is a list of dicts with 'company_id', 'company_name', 'size', 'industry', 'location', 'decision_makers' (empty).

2. For EACH company in the list, ONE AT A TIME:
   - Use web_search to find decision-makers on LinkedIn, Google, and Yahoo. Query: "{company_name} {industry} DFW decision makers HR managers CEOs site:linkedin.com | site:*.org | site:*.com -inurl:(signup | login)".
   - Collect data for at least one decision-maker with these EXACT fields:
     - "name": Full name (string)
     - "role": Job title (string, e.g., "CEO")
     - "email": Email (string, "email@example.com" if not found)
     - "phone": Phone (string, "N/A" if not found)
     - "linkedin_profile": URL (string, "N/A" if not found)
     - "preferred_contact": "Email", "Phone", or "LinkedIn" (string, "N/A" if not found)
     - "last_contact_date": "YYYY-MM-DD" (string, "2025-02-27" if not applicable)
     - "notes": Info (string, "N/A" if none, e.g., "Email not found")

3. IMMEDIATELY update the company with update_decision_makers_tool:
   - Input MUST be a PLAIN JSON string with EXACTLY two top-level keys:
     - "company_id": Integer from fetch_companies_tool
     - "decision_makers": List of dicts with the 8 fields above
   - Example: {"company_id": 7, "decision_makers": [{"name": "Robert Isom", "role": "Chief Executive Officer", "email": "email@example.com", "phone": "N/A", "linkedin_profile": "N/A", "preferred_contact": "N/A", "last_contact_date": "2025-02-27", "notes": "N/A"}]}
   - IMPORTANT: When providing JSON data, follow these formatting rules:
         - Provide clean JSON objects without any additional formatting characters
         - Do NOT wrap the JSON in backticks (e.g., `{"key": "value"}`)
         - Do NOT wrap the JSON in single quotes (e.g., '{"key": "value"}')
         - Do NOT use escaped quotes (e.g., \"key\": \"value\")
         - Do NOT add Markdown formatting (e.g., ```json)
         - JSON should be provided as plain text: {"key": "value"}
   Example of CORRECT JSON format:
   {"company_id": 1, "decision_makers": [{"name": "John Doe", "role": "CEO"}]}

Example of INCORRECT JSON format:
`{"company_id": 1, "decision_makers": [{"name": "John Doe", "role": "CEO"}]}`
   - Call update_decision_makers_tool ONCE per company with a plain JSON string.

Rules:
- Process ONE company at a time: search, collect, update, then next.
- Do NOT batch updates or use a list of companies; update_decision_makers_tool takes ONE company per call.
- Ensure the JSON is PLAIN with NO extra quotes, escapes, or characters beyond the example.
- Continue until ALL companies are updated or the list is exhausted.
- Start IMMEDIATELY with fetch_companies_tool.

If update_decision_makers_tool fails, check the error and ensure the JSON matches the example EXACTLY without extra quotes or escapes.
"""
decision_maker = initialize_agent(
    tools=decision_maker_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    prompt=decision_maker_prompt,
    max_iterations=100,
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
   - Subject line: Attention-grabbing, personalized to company's industry/needs targeting primary decision maker
   - recipient: primary decision maker's email address
   - Email body: Personalized greeting to primary decision maker
      - Brief introduction to your stress management services
      - Industry-specific pain points and how your services address them
      - Clear value proposition with potential ROI for their specific situation
      - Specific call-to-action
      - Professional signature: Restoring Minds Wellness Staff, 717 W. Main St. ,Midlothian, TX 76065, 214-235-9087

5. Update the outreach record using outreach_log with:
   - outreach_id: The numeric ID of the outreach record (int)
   - email_template_data: The generated email template as a dictionary containing:
     {
       "name": "Template name",
       "subject": "Email subject line",
       "recipient": "Primary decision maker's email address",
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
       "recipient": "HRs email address
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
    prompt=outreach_prompt,
    max_iterations=100,
)