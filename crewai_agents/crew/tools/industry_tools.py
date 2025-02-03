from django.db.models import Q
from typing import List, Dict, Optional
from crewai.tools import tool
from django.core.exceptions import ValidationError
from django.apps import apps

"""Populate Competitor Trend Tool"""
@tool("populate_competitor_trend")
def populate_competitor_trend(
    source: str,
    trend_description: str,
    competitor_name: Optional[str] = None,
    impact_level: str = "Medium",
    notes: Optional[str] = None,
) -> str:
    """
    Insert competitor trend data into the 'competitor_trends' table using Django ORM.

    :param source: Source of the trend
    :param trend_description: Description of the trend
    :param competitor_name: Name of the competitor (optional)
    :param impact_level: Impact level of the trend (default: "Medium")
    :param notes: Additional notes (optional)
    :return: A success or failure message
    """
    from django.apps import apps
    CompetitorTrend = apps.get_model('crewai_agents', 'CompetitorTrend')
    try:
        new_trend = CompetitorTrend(
            source=source,
            trend_description=trend_description,
            competitor_name=competitor_name,
            impact_level=impact_level,
            notes=notes,
        )
        new_trend.full_clean()
        new_trend.save()
        return "Competitor trend data populated successfully."
    except ValidationError as e:
        return f"Failed to populate competitor trend data due to validation error: {str(e)}"
    except Exception as e:
        return f"Failed to populate competitor trend data: {str(e)}"
    
    
"""Get Competitor Trends Data Tool"""
@tool("get_competitor_trends_data")
def get_competitor_trends_data(
    competitor_name: Optional[str] = None,
    impact_level: Optional[str] = None,
    source: Optional[str] = None,
) -> List[Dict]:
    """
    Retrieve competitor trend data based on provided filters (competitor_name, impact_level, source) using Django ORM.

    :param competitor_name: Name of the competitor to filter (optional)
    :param impact_level: Impact level to filter (optional)
    :param source: Source of the trend to filter (optional)
    :return: A list of competitor trend data matching the criteria
    """
    from django.apps import apps
    CompetitorTrend = apps.get_model('crewai_agents', 'CompetitorTrend')
    try:
        query = Q()
        if competitor_name:
            query &= Q(competitor_name__icontains=competitor_name)
        if impact_level:
            query &= Q(impact_level=impact_level)
        if source:
            query &= Q(source__icontains=source)

        trends = CompetitorTrend.objects.filter(query)

        results = []
        for trend in trends:
            trend_data = {
                "trend_id": trend.trend_id,
                "date": trend.date,
                "source": trend.source,
                "trend_description": trend.trend_description,
                "competitor_name": trend.competitor_name,
                "impact_level": trend.impact_level,
                "notes": trend.notes,
            }
            results.append(trend_data)

        return results
    except Exception as e:
        return {"error": f"Failed to retrieve competitor trend data: {str(e)}"}