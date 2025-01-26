from django.db.models import Q
from typing import List, Dict
from crewai.tools import tool
from django.core.exceptions import ValidationError
from django.apps import apps

"""Populate Outreach Tool"""
@tool("populate_outreach")
def populate_outreach(
    contact_id: int,
    outreach_method: str,
    template_used: str,
    response_status: str = "No Response",
    follow_up_date: str = None,
    notes: str = None,
) -> str:
    """
    Insert outreach data into the 'outreach' table using Django ORM.

    :param contact_id: ID of the contact person
    :param outreach_method: Method of outreach (e.g., "Email", "LinkedIn")
    :param template_used: Template used for outreach
    :param response_status: Response status (default: "No Response")
    :param follow_up_date: Follow-up date (optional)
    :param notes: Additional notes (optional)
    :return: A success or failure message
    """
    from django.apps import apps
    Outreach = apps.get_model('crewai_agents', 'Outreach')
    try:
        new_outreach = Outreach(
            contact_id=contact_id,
            outreach_method=outreach_method,
            template_used=template_used,
            response_status=response_status,
            follow_up_date=follow_up_date,
            notes=notes,
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