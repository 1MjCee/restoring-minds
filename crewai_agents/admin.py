from django.contrib import admin
from .models import SiteUser, Tool, Agent, Task, Crew, Company, ContactPerson, Outreach, CompetitorTrend, PricingTier
from unfold.admin import ModelAdmin
from django.contrib import messages
from .models import Crew
from django.utils.html import format_html
from django.urls import path, reverse
import subprocess
import os 

"""Crew Admin"""
@admin.register(Crew)
class CrewAdmin(ModelAdmin):
    list_display = ('name', 'process', 'verbose', 'run_button', 'stop_button')
    filter_horizontal = ('agents', 'tasks')
    ordering = ('name',)

    def run_button(self, obj):
        return format_html(
            '<a class="button button-primary" href="{}">Run</a>',
            reverse('admin:run_script', args=[obj.pk])
        )
    run_button.short_description = "Run Crew"

    # Stop Button
    def stop_button(self, obj):
        return format_html(
            '<a class="button button-danger" href="{}">Stop</a>',
            reverse('admin:stop_script', args=[obj.pk])
        )
    stop_button.short_description = "Stop Crew"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('run-script/<int:crew_id>/', self.run_script_view, name='run_script'),
            path('stop-script/<int:crew_id>/', self.stop_script_view, name='stop_script'),
        ]
        return custom_urls + urls

    def run_script_view(self, request, crew_id):
        try:
            # Check if the script is already running
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            main_script_path = os.path.join(project_root, 'crewai_agents', 'crew', 'main.py')
            
            # Check if the script is already running
            script_process = subprocess.run(
                ["pgrep", "-f", "main.py"], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            if script_process.returncode == 0:
                messages.info(request, f"Crew {crew_id} is already running.")
            else:
                subprocess.run(["python3", main_script_path], check=True)
                messages.success(request, f"Crew {crew_id} executed successfully!")
        except subprocess.CalledProcessError as e:
            messages.error(request, f"Error executing crew {crew_id}: {str(e)}")
        except Exception as e:
            messages.error(request, f"Unexpected error: {str(e)}")
        
        return self.response_post_save_change(request, None)


    def stop_script_view(self, request, crew_id):
        try:
            # Check if the script is running before stopping
            script_process = subprocess.run(
                ["pgrep", "-f", "main.py"], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            
            if script_process.returncode == 0:
                # Stop the script if it's running
                subprocess.run(["pkill", "-f", "main.py"], check=True)
                messages.success(request, f"Crew {crew_id} stopped successfully!")
            else:
                messages.info(request, f"Crew {crew_id} not running.")
        except Exception as e:
            messages.error(request, f"Error stopping script for crew {crew_id}: {str(e)}")
        
        return self.response_post_save_change(request, None)


""" Site User Admin """
@admin.register(SiteUser)
class SiteUserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

""" Tool Admin """
@admin.register(Tool)
class ToolAdmin(ModelAdmin):
    list_display = ('name', 'type', 'description')
    search_fields = ('name', 'type')
    ordering = ('name',)

""" Agent Admin """
@admin.register(Agent)
class AgentAdmin(ModelAdmin):
    list_display = ('name', 'role', 'goal', 'get_tools')
    search_fields = ('name', 'role')
    filter_horizontal = ('tools',)
    ordering = ('name',)

    def get_tools(self, obj):
        return ", ".join([tool.name for tool in obj.tools.all()])
    get_tools.short_description = 'Tools'
    list_per_page = 10

""" Task Admin """
@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('order', 'name', 'description', 'expected_output', 'get_context_tasks', 'assigned_agent')
    search_fields = ('name', 'assigned_agent__name')
    ordering = ('name',)

    def get_context_tasks(self, obj):
        return ", ".join([task.name for task in obj.context.all()])
    
    get_context_tasks.short_description = 'Context Tasks'
    list_per_page = 10

    
""" Company Admin """
@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ('company_name', 'employee_size', 'industry', 'location', 'website_url', 'revenue_growth', 'stress_level_score', 'wellness_culture_score', 'priority_score', 'last_updated')
    search_fields = ('company_name', 'industry', 'location')
    list_filter = ('industry', 'location')
    ordering = ('company_name',)
    list_per_page = 10


""" Contact Person Admin """
@admin.register(ContactPerson)
class ContactPersonAdmin(ModelAdmin):
    list_display = ('name', 'company', 'role', 'email', 'phone', 'linkedin_profile', 'preferred_contact_method', 'last_contact_date')
    search_fields = ('name', 'company__company_name', 'role')
    list_filter = ('preferred_contact_method', 'company__industry')
    ordering = ('name',)
    list_per_page = 10


""" Outreach Admin """
@admin.register(Outreach)
class OutreachAdmin(ModelAdmin):
    list_display = ('company', 'message_type', 'message', 'outreach_date', 'response_status', 'follow_up_date', 'comments')
    search_fields = ('message_type', 'response_status')
    list_filter = ('message_type', 'response_status')
    ordering = ('outreach_date',)
    list_per_page = 10


""" Competitor Trend Admin """
@admin.register(CompetitorTrend)
class CompetitorTrendAdmin(ModelAdmin):
    list_display = ('trend_id', 'date', 'source', 'trend_description', 'competitor_name', 'impact_level')
    search_fields = ('source', 'trend_description', 'competitor_name')
    list_filter = ('impact_level', 'date')
    ordering = ('date',)
    list_per_page = 10

""" Pricing Tier Admin """
@admin.register(PricingTier)
class PricingTierAdmin(ModelAdmin):
    list_display = ('min_employees', 'max_employees', 'price', 'features')
    search_fields = ('features',)
    list_filter = ('price',)
