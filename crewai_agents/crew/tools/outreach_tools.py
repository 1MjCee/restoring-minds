from django.db.models import Q
from typing import List, Dict, Optional
from crewai.tools import tool
from django.core.exceptions import ValidationError
from django.apps import apps

"""Populate Outreach Tool"""
@tool("populate_outreach")
def populate_outreach(
    company_id: int,
    message: str,
    response_status: str,
    follow_up_date: Optional[str] = None,
    comments: Optional[str] = None,
    message_type: str = 'Email',
    outreach_date: Optional[str] = None,
) -> str:
    """
    Insert outreach data into the 'outreach' table using Django ORM.

    Args:
        company_id (int): ID of the company associated with the outreach.
        outreach_date (str): Date of the outreach in string format (e.g., "YYYY-MM-DD").
        message_type (str): Type of message used for outreach (e.g., "Email", "LinkedIn").
        message (str): The content of the outreach message.
        response_status (str, optional): Status of the response to the outreach. Defaults to "No Response".
        follow_up_date (str, optional): Date for a follow-up action, if applicable. Defaults to None.
        comments (str, optional): Additional notes or comments related to the outreach. Defaults to None.

    Returns:
        str: A success or failure message indicating the outcome of the operation.
    """
    from django.apps import apps
    Outreach = apps.get_model('crewai_agents', 'Outreach')
    try:
        new_outreach = Outreach(
            company_id=company_id,
            outreach_date=outreach_date,
            message_type=message_type,
            message=message,
            response_status=response_status,
            follow_up_date=follow_up_date,
            comments=comments,
        )
        new_outreach.full_clean()
        new_outreach.save()
        return "Outreach data populated successfully."
    except ValidationError as e:
        return f"Failed to populate outreach data due to validation error: {str(e)}"
    except Exception as e:
        return f"Failed to populate outreach data: {str(e)}"


"""Get Outreach Data Tool"""
@tool("get_outreach_data")
def get_outreach_data(
    contact_id: int = None,
    response_status: str = None,
    outreach_method: str = None,
) -> List[Dict]:
    """
    Retrieve outreach data based on provided filters (contact_id, response_status, outreach_method) using Django ORM.

    :param contact_id: ID of the contact person to filter (optional)
    :param response_status: Response status to filter (optional)
    :param outreach_method: Outreach method to filter (optional)
    :return: A list of outreach data matching the criteria
    """
    from django.apps import apps
    Outreach = apps.get_model('crewai_agents', 'Outreach')
    try:
        query = Q()
        if contact_id:
            query &= Q(contact_id=contact_id)
        if response_status:
            query &= Q(response_status=response_status)
        if outreach_method:
            query &= Q(outreach_method=outreach_method)

        outreach_attempts = Outreach.objects.filter(query).select_related("contact")

        results = []
        for outreach in outreach_attempts:
            outreach_data = {
                "outreach_id": outreach.outreach_id,
                "contact_name": outreach.contact.name,
                "outreach_method": outreach.outreach_method,
                "template_used": outreach.template_used,
                "response_status": outreach.response_status,
                "follow_up_date": outreach.follow_up_date,
                "notes": outreach.notes,
            }
            results.append(outreach_data)

        return results
    except Exception as e:
        return {"error": f"Failed to retrieve outreach data: {str(e)}"}