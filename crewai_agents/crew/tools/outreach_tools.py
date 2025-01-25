from crewai.tools import BaseTool
import json

"""PersonalizedTemplateGenerator Tool"""
class PersonalizedTemplateGenerator(BaseTool):
    name = "PersonalizedTemplateGenerator"
    description = "Generates personalized email and LinkedIn message templates based on lead data."

    def _run(self, lead_data: dict) -> str:
        # Example logic to generate email template
        email_template = f"""
        Subject: Stress Management Solutions for {lead_data['company_name']}

        Dear {lead_data['contact_name']},

        We've noticed that {lead_data['company_name']} has been experiencing rapid growth in DFW,
        which often comes with its own set of challenges, including stress management.
        
        Our tailored solutions could help in alleviating these pressures...

        Best regards,
        [Your Name]
        """

        # Example logic to generate LinkedIn message
        linkedin_template = f"""
        Hi {lead_data['contact_name']},

        I came across your profile while researching fast-growing companies in DFW.
        I believe our stress management solutions could significantly benefit {lead_data['company_name']}. 
        
        May we have a brief call to discuss this?

        Best,
        [Your Name]
        """

        return json.dumps({
            "email": email_template,
            "linkedin": linkedin_template
        })



"""LeadPrioritizer Tool"""
class LeadPrioritizer(BaseTool):
    name = "LeadPrioritizer"
    description = "Prioritizes leads based on their potential for outreach success."

    def _run(self, leads: list) -> list:
        # Example scoring system - this is highly simplified
        prioritized_leads = sorted(leads, key=lambda lead: (
            lead['decision_maker_accessibility'] +  
            lead['company_growth_rate'] * 2 +       
            lead['relevance_score']                 
        ), reverse=True)

        return json.dumps(prioritized_leads)



"""MarketMonitor Tool"""
class MarketMonitor(BaseTool):
    name = "MarketMonitor"
    description = "Monitors the stress management market for changes and trends."

    def _run(self) -> str:
        new_companies = ["TechStressor Inc.", "CalmCorp"]
        competitor_changes = {
            "HealthyMind": "Launched new stress app",
            "FocusNow": "Price drop on services"
        }
        market_trends = ["Increasing demand for remote work stress solutions", "Shift towards wellness programs"]

        weekly_alert = {
            "New Companies": new_companies,
            "Competitor Changes": competitor_changes,
            "Market Trends": market_trends
        }

        return json.dumps(weekly_alert)