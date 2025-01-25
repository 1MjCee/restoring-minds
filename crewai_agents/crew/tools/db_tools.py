from django.db.models import Q
from typing import List, Dict
from crewai.tools import tool
from django.core.exceptions import ValidationError
from django.apps import apps
# Company = apps.get_model('crewai_agents', 'Company')

# from django.apps import apps
# ContactPerson = apps.get_model('crewai_agents', 'ContactPerson')


"""Populate Companies Tool"""
@tool("populate_companies")
def populate_companies(company_name: str, employee_size: int, industry: str, location: str, website_url: str, targeting_reason: str) -> str:
    """
    Insert company data into the 'companies' table using Django ORM.

    :param company_name: Name of the company
    :param employee_size: Number of employees
    :param industry: Industry sector
    :param location: Location of the company
    :param website_url: Company's website URL
    :param targeting_reason: Reason for targeting this company
    :return: A success or failure message
    """
    from django.apps import apps
    Company = apps.get_model('crewai_agents', 'Company')
    try:
        new_company = Company(
            company_name=company_name, 
            employee_size=employee_size, 
            industry=industry, 
            location=location, 
            website_url=website_url, 
            targeting_reason=targeting_reason
        )
        new_company.full_clean() 
        new_company.save()  
        return "Company data populated successfully."
    except ValidationError as e:
        return f"Failed to populate company data due to validation error: {str(e)}"
    except Exception as e:
        return f"Failed to populate company data: {str(e)}"


"""Populate Contact Persons Tool"""
@tool("populate_contact_persons")
def populate_contact_persons(name: str, role: str, email: str, phone: str, company_id: int) -> str:
    """
    Insert contact person data into the 'contact_persons' table using Django ORM.

    :param name: Name of the contact person
    :param role: Role of the contact person
    :param email: Email address of the contact person
    :param phone: Phone number of the contact person (can be None)
    :param company_id: ID of the company to which this contact belongs
    :return: A success or failure message
    """
    from django.apps import apps
    ContactPerson = apps.get_model('crewai_agents', 'ContactPerson')
    try:
        new_contact = ContactPerson(
            name=name, 
            role=role, 
            email=email, 
            phone=phone, 
            company_id=company_id
        )
        new_contact.full_clean()  
        new_contact.save()
        return "Contact person data populated successfully."
    except ValidationError as e:
        return f"Failed to populate contact person data due to validation error: {str(e)}"
    except Exception as e:
        return f"Failed to populate contact person data: {str(e)}"

"""Get Companies Data Tool"""
@tool("get_companies_data")
def get_companies_data(company_name: str = None, industry: str = None, location: str = None) -> List[Dict]:
    """
    Retrieve company data based on provided filters (company_name, industry, location) using Django ORM.

    :param company_name: Name of the company to search (optional)
    :param industry: Industry type to filter companies (optional)
    :param location: Location of the company to filter (optional)
    :return: A list of company data matching the criteria
    """
    from django.apps import apps
    Company = apps.get_model('crewai_agents', 'Company')
    ContactPerson = apps.get_model('crewai_agents', 'ContactPerson')
    try:
        # Build the query using Django's Q objects for dynamic filtering
        query = Q()
        if company_name:
            query &= Q(company_name__icontains=company_name)
        if industry:
            query &= Q(industry__icontains=industry)
        if location:
            query &= Q(location__icontains=location)

        # Fetch matching results
        companies = Company.objects.filter(query)

        # Prepare results
        results = []
        for company in companies:
            company_data = {
                "company_name": company.company_name,
                "employee_size": company.employee_size,
                "industry": company.industry,
                "location": company.location,
                "website_url": company.website_url,
                "targeting_reason": company.targeting_reason,
                "contacts": [
                    {
                        "name": contact.name,
                        "role": contact.role,
                        "email": contact.email,
                        "phone": contact.phone
                    }
                    for contact in company.contact_persons.all() 
                ]
            }
            results.append(company_data)

        return results
    except Exception as e:
        return {"error": f"Failed to retrieve company data: {str(e)}"}