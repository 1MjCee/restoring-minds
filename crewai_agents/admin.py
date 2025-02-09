from django.contrib import admin
from .models import SiteUser, Tool, Agent, Task, Crew, Company, ContactPerson, Outreach, CompetitorTrend, PricingTier
from unfold.admin import ModelAdmin
from django.contrib import messages
from .models import Crew
from django.utils.html import format_html
from django.urls import path, reverse
import subprocess
import os
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .CustomAdmins import CrewAdmin

admin.site.site_header = "Restoring Minds Admin"
admin.site.site_title = "Restoring Minds Admin Portal"
admin.site.index_title = "Welcome to Restoring Minds Admin Portal"

"""Crew Admin"""
admin.site.register(Crew, CrewAdmin)


""" Site User Admin """
@admin.register(SiteUser)
class SiteUserAdmin(BaseUserAdmin, ModelAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

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
