from langchain.tools import BaseTool
from django.db import transaction
from langchain.tools import Tool
from django.apps import apps
import json
import ast
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class CompanyUpdateTool(BaseTool):
    name: str = "company_update"
    description: str = "Updates or creates a company record in the database. Input should be a dict with keys: company_name (str), size (int), industry (str), location (str), stress_score (float, optional)"

    def _run(self, input_data):
        print(f"DEBUG - Input data type: {type(input_data)}")
        print(f"DEBUG - Input data raw: {repr(input_data)}")
        
        # Force parsing if the input is passed as a string
        if isinstance(input_data, str):
            print(f"DEBUG - Input is string, attempting to parse")
            # Try multiple parsing methods
            try:
                # Try json.loads (standard JSON parser)
                input_data = json.loads(input_data)
                print(f"DEBUG - Parsed with json.loads: {input_data}")
            except json.JSONDecodeError as e:
                print(f"DEBUG - JSON decode error: {str(e)}")
                try:
                    # Try ast.literal_eval (Python literal parser)
                    import ast
                    input_data = ast.literal_eval(input_data)
                    print(f"DEBUG - Parsed with ast.literal_eval: {input_data}")
                except Exception as e:
                    print(f"DEBUG - ast parse error: {str(e)}")
                    # Last resort: manual string cleaning and parsing
                    try:
                        # Replace single quotes with double quotes
                        fixed_json = input_data.replace("'", '"')
                        input_data = json.loads(fixed_json)
                        print(f"DEBUG - Parsed with manual fix: {input_data}")
                    except Exception as e:
                        print(f"DEBUG - Manual fix error: {str(e)}")
                        return f"Error: Could not parse input: {repr(input_data)}"

        # After parsing attempts, ensure input_data is a dict
        if not isinstance(input_data, dict):
            print(f"DEBUG - Final input is not a dict: {type(input_data)}")
            return "Error: Input data is not a valid dictionary after parsing."
        
        print(f"DEBUG - Final parsed input: {input_data}")

        try:
            Company = apps.get_model('crewai_agents', 'Company')
            with transaction.atomic():
                # Get the actual field names from the model to check
                field_names = [field.name for field in Company._meta.get_fields()]
                print(f"DEBUG - Available fields: {field_names}")
                
                # Use the correct field names based on your model
                company, created = Company.objects.update_or_create(
                    company_name=input_data["company_name"],
                    defaults={
                        "employee_size": input_data["size"],
                        "industry": input_data["industry"],
                        "location": input_data["location"],
                        "stress_level_score": input_data.get("stress_score", 0)
                    }
                )
            return f"Company {'created' if created else 'updated'}: {input_data['company_name']}"
        except Exception as e:
            print(f"DEBUG - Exception in database operation: {str(e)}")
            return f"Error: {str(e)}"


class CompetitorTrendTool(BaseTool):
    name: str = "competitor_trend_update"
    description: str = "Logs competitor trends for analysis. Input should be a dict with keys: competitor_name (str), trend_description (str), impact_level (str)."

    def _run(self, input_data):        
        # Handle different input types
        if isinstance(input_data, str):
            # If the input is already a string containing quotes
            if input_data.startswith("'") and input_data.endswith("'"):
                # Remove the outer quotes
                input_data = input_data[1:-1]
                print(f"DEBUG - Removed outer quotes: {input_data}")
                
            try:
                # Try parsing as JSON
                input_data = json.loads(input_data)
                print(f"DEBUG - Parsed with json.loads: {input_data}")
            except json.JSONDecodeError:
                try:
                    # Try parsing as Python literal
                    import ast
                    input_data = ast.literal_eval(input_data)
                    print(f"DEBUG - Parsed with ast.literal_eval: {input_data}")
                except Exception as e:
                    print(f"DEBUG - Parsing error: {str(e)}")
                    try:
                        # Final attempt: convert single quotes to double quotes
                        input_data = json.loads(input_data.replace("'", '"'))
                        print(f"DEBUG - Parsed after quote replacement: {input_data}")
                    except Exception as e2:
                        print(f"DEBUG - Final parsing error: {str(e2)}")
                        return "Error: Input string is not valid JSON."

        # Ensure input_data is a dict after deserialization
        if not isinstance(input_data, dict):
            print(f"DEBUG - Input is not a dict: {type(input_data)}")
            return "Error: Input data is not a valid dictionary."

        print(f"DEBUG - Final parsed input: {input_data}")

        # Create the CompetitorTrend object
        CompetitorTrend = apps.get_model('crewai_agents', 'CompetitorTrend')
        
        try:
            trend = CompetitorTrend.objects.create(
                competitor_name=input_data["competitor_name"],
                trend_description=input_data["trend_description"],
                impact_level=input_data["impact_level"]
            )

            # Print the trend object for debugging
            print(f"Logged trend: {trend}")

            # Returning success message with trend info (ensure 'id' exists)
            if hasattr(trend, 'id'):
                return f"Logged trend for {input_data['competitor_name']}: {trend.id}"
            else:
                return f"Logged trend for {input_data['competitor_name']} (no ID found)"
        except Exception as e:
            print(f"DEBUG - Exception in trend creation: {str(e)}")
            return f"Error: {str(e)}"


class OutreachLogTool(BaseTool):
    name: str = "outreach_log"
    description: str = """
    Update an existing outreach record's email foreign key with a new email template.
    Expects input dict with: outreach_id (int), email_template_data (dict with 'name', 'subject', 'content', optionally 'recipient'), status (str, optional).
    Creates a new Email record and links it to the Outreach identified by outreach_id.
    """

    def _run(self, input_data):
        print(f"DEBUG - Raw input: {repr(input_data)}")
        
        # Handle string input from the agent
        if isinstance(input_data, str):
            try:
                input_data = json.loads(input_data)
            except json.JSONDecodeError:
                try:
                    import ast
                    input_data = ast.literal_eval(input_data)
                except (ValueError, SyntaxError):
                    return "Error: Input string is not valid JSON or dictionary."

        # Ensure input_data is a dict
        if not isinstance(input_data, dict):
            return "Error: Input data must be a dictionary."

        # Extract required fields
        try:
            outreach_id = input_data["outreach_id"]
            email_template_data = input_data.get("email_template_data")
            status = 'updated'
        except KeyError as e:
            return f"Error: Missing required field {str(e)} in input: {repr(input_data)}"

        Outreach = apps.get_model('crewai_agents', 'Outreach')
        Email = apps.get_model('crewai_agents', 'Email')
        
        try:
            # Get the existing outreach record
            outreach = Outreach.objects.get(outreach_id=outreach_id)
            
            # Handle email update
            if email_template_data:
                # Create a new Email record based on your Email model
                email = Email.objects.create(
                    name=email_template_data.get("name", f"Email for {outreach.company.company_name}"),
                    recipient=email_template_data.get("recipient", None),  # Optional, nullable
                    subject=email_template_data.get("subject", f"Introduction to {outreach.company.company_name}"),
                    content=email_template_data.get("content", "Default content placeholder"),
                    is_active=True,
                    is_default=email_template_data.get("is_default", True)  
                )
                # Update the outreach record's email foreign key
                outreach.email = email
                if status: 
                    outreach.status = status
                outreach.save()
                return f"Updated outreach {outreach.outreach_id} with email ID {email.id}"
            else:
                return "Error: No email_template_data provided to update the email."

        except Outreach.DoesNotExist:
            return f"Error: Outreach with ID {outreach_id} not found."
        except Exception as e:
            return f"Error updating outreach: {str(e)}"

    def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported yet.")


def fetch_outreach_data(outreach_id):
    """Fetch outreach data and associated company details using an outreach_id."""
    if isinstance(outreach_id, str):
        try:
            data = json.loads(outreach_id)
            if isinstance(data, dict) and 'outreach_id' in data:
                outreach_id = data['outreach_id']
        except json.JSONDecodeError:
            if outreach_id.isdigit():
                outreach_id = int(outreach_id)
            else:
                return f"Error: Invalid outreach_id format: {outreach_id}. Please provide a numeric outreach ID."

    try:
        Outreach = apps.get_model('crewai_agents', 'Outreach')
        outreach = Outreach.objects.get(outreach_id=outreach_id)  
        company = outreach.company
 
        
        return {
            'outreach_id': outreach.outreach_id,
            'company_id': company.id,
            'company_name': company.company_name,
            'industry': company.industry,
            'size': company.employee_size,
            'location': company.location,
            'decision_makers': company.decision_makers if company.decision_makers else {},
            'outreach_status': outreach.status,
            'outreach_email_id': outreach.email.id if outreach.email else None,
            'outreach_date': str(outreach.outreach_date) if outreach.outreach_date else None
        }
    except Outreach.DoesNotExist:
        return f"Outreach with ID {outreach_id} not found."
    except LookupError:
        return "Error: Model not found in app registry. Check app label."
    except Exception as e:
        return f"Error fetching outreach data: {str(e)}"

fetch_outreach_data_tool = Tool(
    name="fetch_outreach_data",
    description="Fetch existing outreach data and its associated company details. Provide the outreach_id as an integer (e.g., 1).",
    func=fetch_outreach_data
)

def fetch_pending_outreach_ids(dummy_input=None):
    """Fetch a list of all outreach IDs that have status 'pending'."""
    try:
        Outreach = apps.get_model('crewai_agents', 'Outreach')
        
        # Query for outreach records with 'pending' status (case-sensitive to match default)
        pending_outreaches = Outreach.objects.filter(status='pending')
        
        # Extract outreach IDs
        outreach_ids = [outreach.outreach_id for outreach in pending_outreaches]  # Use outreach_id field
        
        if not outreach_ids:
            return "No outreach records with pending status found."
        
        return {
            'count': len(outreach_ids),
            'outreach_ids': outreach_ids
        }
    except Exception as e:
        return f"Error fetching pending outreach IDs: {str(e)}"

fetching_pending_outreach_ids = Tool(
    name="fetch_pending_outreaches",
    description="Fetch a list of all outreach IDs that have status 'pending'.",
    func=fetch_pending_outreach_ids
)

def fetch_companies_without_decision_makers(_=None):
    try:
        Company = apps.get_model('crewai_agents', 'Company')  
        companies = Company.objects.filter(decision_makers__in=[[], None])
        if not companies.exists():
            return "No companies found without decision-makers."
        
        result = []
        for company in companies:
            result.append({
                'company_id': company.id,
                'company_name': company.company_name,
                'size': company.employee_size,
                'industry': company.industry,
                'location': company.location,
                'decision_makers': company.decision_makers if company.decision_makers else []
            })
        return result
    except LookupError:
        return "Error: Model 'Company' not found in app registry. Check app label."
    except Exception as e:
        return f"Error fetching companies: {str(e)}"

fetch_companies_tool = Tool(
    name="fetch_companies_without_decision_makers",
    description="Fetches a list of companies with no decision-makers in their decision_makers JSON field.",
    func=fetch_companies_without_decision_makers
)

def update_decision_makers(input_str):
    print(f"DEBUG - Raw input: {repr(input_str)}")  
    
    if isinstance(input_str, str):
        input_str = input_str.strip()
        if input_str.startswith("```json"):
            input_str = input_str[7:]
        elif input_str.startswith("```"):
            input_str = input_str[3:]
        if input_str.endswith("```"):
            input_str = input_str[:-3]
        input_str = input_str.strip()
        print(f"DEBUG - Stripped input: {repr(input_str)}")
    
    try:
        data = json.loads(input_str)
        print(f"DEBUG - Parsed data: {data}")
        
        company_id = data['company_id']
        decision_makers = data['decision_makers']
        
        # Normalize 'title' to 'role' to match model expectations
        for dm in decision_makers:
            if 'title' in dm and 'role' not in dm:
                dm['role'] = dm.pop('title')
                print(f"DEBUG - Normalized 'title' to 'role': {dm}")
        
        Company = apps.get_model('crewai_agents', 'Company')
        company = Company.objects.get(id=company_id)
        company.decision_makers = decision_makers
        company.save()
        return f"Updated decision_makers for {company.company_name} (ID: {company_id})"
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON input: {repr(input_str)} - {str(e)}"
    except KeyError as e:
        return f"Error: Missing required field {str(e)} in input: {repr(input_str)}"
    except ObjectDoesNotExist:
        return f"Error: Company with ID {company_id} not found."
    except Exception as e:
        return f"Error updating company ID {company_id}: {str(e)}"

update_decision_makers_tool = Tool(
    name="update_decision_makers",
    description="Updates the decision_makers JSON field for a company. Input is a JSON string with 'company_id' (int) and 'decision_makers' (list of dicts with 'name', 'role', 'email', 'phone', 'linkedin_profile', 'preferred_contact', 'last_contact_date', 'notes').",
    func=update_decision_makers
)