from crewai_agents.models import Agent, Task, SiteUser, Crew
from django.utils.timezone import now
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect

def dashboard_callback(request, context):
    # Get today's date
    today = now().date()

    # Statistics calculations
    context.update({
        'num_agents': Agent.objects.all().count(),
        'num_tasks': Task.objects.all().count(),
        'num_users': SiteUser.objects.all().count(),
        'num_crew': Crew.objects.all().count(),
    })

    # Create a list of cards for the dashboard
    context['cards'] = [
        {'title': 'Number of Agents', 'value': context['num_agents']},
        {'title': 'Number of Tasks', 'value': context['num_tasks']},
        {'title': 'Number of Users', 'value': context['num_users']},
        {'title': 'Number of Crews', 'value': context['num_crew']},
    ]
    return context

@staff_member_required
def dashboard(request):
    context = dashboard_callback(request, {})
    return render(request, 'admin/dashboard.html', context)