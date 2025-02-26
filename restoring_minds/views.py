from crewai_agents.models import  SiteUser
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from crewai_agents.models import Company, Outreach

def dashboard_callback(request, context):
    # Get today's date
    today = now().date()

    # Statistics calculations
    context.update({
        'prospects': Company.objects.all().count(),
        'prospects_today': Company.objects.filter(created_at=today).count(),
        'outreachs': Outreach.objects.all().count(),
        'outreach_today': Outreach.objects.filter(created_at=today).count(),
        'completed_outreachs': Outreach.objects.filter(status='completed').count(),
    })

    # Create a list of cards for the dashboard
    context['cards'] = [
        {'title': 'Total Prospects', 'value': context['prospects']},
        {'title': 'Today\'s Prospects', 'value': context['prospects_today']},
        {'title': 'Total Outreach Efforts', 'value': context['outreachs']},
        {'title': 'Today\'s Outreach Efforts', 'value': context['outreach_today']},
        {'title': 'Completed Outreach Efforts', 'value': context['completed_outreachs']},
    ]
    return context

@staff_member_required
def dashboard(request):
    context = dashboard_callback(request, {})
    return render(request, 'admin/dashboard.html', context)