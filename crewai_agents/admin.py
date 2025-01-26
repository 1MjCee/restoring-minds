from django.contrib import admin
from .models import SiteUser, Tool, Agent, Task, Crew, Company, ContactPerson, Outreach, CompetitorTrend, SuccessMetric
from unfold.admin import ModelAdmin

@admin.register(SiteUser)
class SiteUserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

@admin.register(Tool)
class ToolAdmin(ModelAdmin):
    list_display = ('name', 'type', 'description')
    search_fields = ('name', 'type')
    ordering = ('name',)

@admin.register(Agent)
class AgentAdmin(ModelAdmin):
    list_display = ('name', 'role', 'goal', 'verbose', 'memory', 'llm')
    search_fields = ('name', 'role')
    filter_horizontal = ('tools',)
    ordering = ('name',)

@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('order', 'name', 'description', 'expected_output', 'get_context_tasks', 'assigned_agent')
    search_fields = ('name', 'assigned_agent__name')
    ordering = ('name',)

    def get_context_tasks(self, obj):
        return ", ".join([task.name for task in obj.context.all()])
    
    get_context_tasks.short_description = 'Context Tasks'

@admin.register(Crew)
class CrewAdmin(ModelAdmin):
    list_display = ('name', 'process', 'verbose')
    filter_horizontal = ('agents', 'tasks')
    ordering = ('name',)

@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ('company_name', 'employee_size', 'industry', 'location', 'website_url', 'revenue_growth', 'stress_level_score', 'wellness_culture_score', 'priority_score', 'last_updated')
    search_fields = ('company_name', 'industry', 'location')
    list_filter = ('industry', 'location')
    ordering = ('company_name',)

@admin.register(ContactPerson)
class ContactPersonAdmin(ModelAdmin):
    list_display = ('name', 'company', 'role', 'email', 'phone', 'linkedin_profile', 'preferred_contact_method', 'last_contact_date')
    search_fields = ('name', 'company__company_name', 'role')
    list_filter = ('preferred_contact_method', 'company__industry')
    ordering = ('name',)

@admin.register(Outreach)
class OutreachAdmin(ModelAdmin):
    list_display = ('outreach_id', 'contact', 'outreach_date', 'outreach_method', 'response_status', 'follow_up_date')
    search_fields = ('contact__name', 'outreach_method', 'response_status')
    list_filter = ('outreach_method', 'response_status')
    ordering = ('outreach_date',)

@admin.register(CompetitorTrend)
class CompetitorTrendAdmin(ModelAdmin):
    list_display = ('trend_id', 'date', 'source', 'trend_description', 'competitor_name', 'impact_level')
    search_fields = ('source', 'trend_description', 'competitor_name')
    list_filter = ('impact_level', 'date')
    ordering = ('date',)

@admin.register(SuccessMetric)
class SuccessMetricAdmin(ModelAdmin):
    list_display = ('case_study_id', 'company_name', 'industry', 'program_description', 'roi', 'productivity_gains', 'employee_retention')
    search_fields = ('company_name', 'industry')
    list_filter = ('industry',)
    ordering = ('company_name',)