from django.db.models import Q
from typing import List, Dict
from crewai.tools import tool
from django.core.exceptions import ValidationError
from django.apps import apps

"""Populate Success Metric Tool"""
@tool("populate_success_metric")
def populate_success_metric(
    company_name: str,
    industry: str,
    program_description: str,
    roi: float = None,
    productivity_gains: float = None,
    employee_retention: float = None,
    notes: str = None,
) -> str:
    """
    Insert success metric data into the 'success_metrics' table using Django ORM.

    :param company_name: Name of the company
    :param industry: Industry of the company
    :param program_description: Description of the program
    :param roi: Return on investment (optional)
    :param productivity_gains: Productivity gains (optional)
    :param employee_retention: Employee retention rate (optional)
    :param notes: Additional notes (optional)
    :return: A success or failure message
    """
    from django.apps import apps
    SuccessMetric = apps.get_model('crewai_agents', 'SuccessMetric')
    try:
        new_metric = SuccessMetric(
            company_name=company_name,
            industry=industry,
            program_description=program_description,
            roi=roi,
            productivity_gains=productivity_gains,
            employee_retention=employee_retention,
            notes=notes,
        )
        new_metric.full_clean()
        new_metric.save()
        return "Success metric data populated successfully."
    except ValidationError as e:
        return f"Failed to populate success metric data due to validation error: {str(e)}"
    except Exception as e:
        return f"Failed to populate success metric data: {str(e)}"
    
"""Get Success Metrics Data Tool"""
@tool("get_success_metrics_data")
def get_success_metrics_data(
    company_name: str = None,
    industry: str = None,
    min_roi: float = None,
    max_roi: float = None,
) -> List[Dict]:
    """
    Retrieve success metric data based on provided filters (company_name, industry, min_roi, max_roi) using Django ORM.

    :param company_name: Name of the company to filter (optional)
    :param industry: Industry to filter (optional)
    :param min_roi: Minimum ROI to filter (optional)
    :param max_roi: Maximum ROI to filter (optional)
    :return: A list of success metric data matching the criteria
    """
    from django.apps import apps
    SuccessMetric = apps.get_model('crewai_agents', 'SuccessMetric')
    try:
        query = Q()
        if company_name:
            query &= Q(company_name__icontains=company_name)
        if industry:
            query &= Q(industry__icontains=industry)
        if min_roi:
            query &= Q(roi__gte=min_roi)
        if max_roi:
            query &= Q(roi__lte=max_roi)

        metrics = SuccessMetric.objects.filter(query)

        results = []
        for metric in metrics:
            metric_data = {
                "case_study_id": metric.case_study_id,
                "company_name": metric.company_name,
                "industry": metric.industry,
                "program_description": metric.program_description,
                "roi": metric.roi,
                "productivity_gains": metric.productivity_gains,
                "employee_retention": metric.employee_retention,
                "notes": metric.notes,
            }
            results.append(metric_data)

        return results
    except Exception as e:
        return {"error": f"Failed to retrieve success metric data: {str(e)}"}