from langchain.tools import BaseTool
from django.db import transaction
from langchain.tools import Tool
from django.apps import apps
import json
import ast

class CompanyUpdateTool(BaseTool):
    name: str = "company_update"
    description: str = "Updates or creates a company record in the database. Input should be a dict with keys: company_name (str), size (int), industry (str), location (str), stress_score (float, optional), decision_makers (dict, optional)."

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
                        # Omitted decision_makers for now to simplify
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
        print(f"DEBUG - Original input: {repr(input_data)}")
        
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
    Log an outreach attempt for a company using an email template.
    If the email_template_id doesn’t exist, create a default email template first.
    Expects input dict with: company_id (int), email_template_id (int), status (str).
    """

    def _run(self, input_data):
        # Force parsing if the input is passed as a string
        if isinstance(input_data, str):
            try:
                # Try JSON first
                input_data = json.loads(input_data)
            except json.JSONDecodeError:
                try:
                    # Try Python literal eval for single-quoted dictionaries
                    import ast
                    input_data = ast.literal_eval(input_data)
                except (ValueError, SyntaxError):
                    return "Error: Input string is not valid JSON or dictionary."

        # Ensure input_data is a dict after deserialization
        if not isinstance(input_data, dict):
            return "Error: Input data is not a valid dictionary after parsing."

        Outreach = apps.get_model('crewai_agents', 'Outreach')
        Company = apps.get_model('crewai_agents', 'Company')
        Email = apps.get_model('crewai_agents', 'Email')
        
        try:
            # Get the company
            company = Company.objects.get(id=input_data["company_id"])
            
            # Handle the email (either use existing or create new)
            if "email_id" in input_data and input_data["email_id"]:
                try:
                    email = Email.objects.get(id=input_data["email_id"])
                except Email.DoesNotExist:
                    return f"Error: Email with ID {input_data['email_id']} not found"
            elif "email_content" in input_data and input_data["email_content"]:
                # Create a new email template with provided content
                email_content = input_data["email_content"]
                email = Email.objects.create(
                    name=email_content.get("name", f"Email for {company.company_name}"),
                    subject=email_content.get("subject", f"Introduction to {company.company_name}"),
                    content=email_content.get("content", "Default content placeholder"),
                    is_active=True
                )
            else:
                # Create a generic template if neither email_id nor email_content provided
                email = Email.objects.create(
                    name=f"Auto-generated for {company.company_name}",
                    subject=f"Introduction to {company.company_name}",
                    content=f"This is an auto-generated email for {company.company_name} in the {company.industry} industry.",
                    is_active=True
                )
            
            # Create the outreach record
            outreach = Outreach.objects.create(
                company=company,
                email=email,
                status=input_data["status"]
            )
            
            return f"Outreach logged: {outreach.outreach_id} with email: {email.id}"
        except Company.DoesNotExist:
            return f"Error: Company with ID {input_data['company_id']} not found"
        except Exception as e:
            return f"Error: {str(e)}"


def fetch_outreach_data(company_id):
    if isinstance(company_id, str):
        try:
            # Try to parse it as JSON
            import json
            data = json.loads(company_id)
            # Extract company_id from the parsed JSON
            if isinstance(data, dict) and 'company_id' in data:
                company_id = data['company_id']
        except json.JSONDecodeError:
            # If it's not valid JSON but might be a digit string
            if company_id.isdigit():
                company_id = int(company_id)
            else:
                return f"Error: Invalid company_id format: {company_id}. Please provide a numeric company ID."

    try:
        Company = apps.get_model('crewai_agents', 'Company') 
        Outreach = apps.get_model('crewai_agents', 'Outreach')

        company = Company.objects.get(id=company_id)
        outreach = Outreach.objects.get(company=company)
        return {
            'company_id': company.id,
            'company_name': company.company_name,
            'industry': company.industry,
            'size': company.employee_size,
            'location': company.location,
            'decision_makers': company.decision_makers if company.decision_makers else {},
            'outreach_status': outreach.status,
            'outreach_email_id': outreach.email.id if outreach.email else None,
            'outreach_date': str(outreach.outreach_date) if outreach.outreach_date else None,
            'outreach_id': outreach.outreach_id
        }
    except Company.DoesNotExist:
        return "Company not found."
    except Outreach.DoesNotExist:
        return "Outreach not found (should exist due to signal)."
    except LookupError:
        return "Error: Model not found in app registry. Check app label."

fetch_outreach_data_tool = Tool(
    name="fetch_outreach_data",
    description="Fetch existing outreach data and its associated company details. Provide the company_id as an integer (e.g., 1).",
    func=fetch_outreach_data
)


def fetch_pending_outreach_ids(dummy_input=None):
    try:
        Outreach = apps.get_model('crewai_agents', 'Outreach')
        
        # Query for outreach records with 'Pending' status
        pending_outreaches = Outreach.objects.filter(status='Pending')
        
        # Extract outreach IDs
        outreach_ids = [outreach.id for outreach in pending_outreaches]
        
        if not outreach_ids:
            return "No outreach records with pending status found."
        
        return {
            'count': len(outreach_ids),
            'outreach_ids': outreach_ids
        }
    except Exception as e:
        return f"Error fetching pending outreach IDs: {str(e)}"

# Create the tool
fetching_pending_outreach_ids = Tool(
    name="fetch_pending_outreaches",
    description="Fetch a list of all outreach IDs that have status 'Pending'.",
    func=fetch_pending_outreach_ids
)