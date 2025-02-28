from django.contrib import admin
from .models import SiteUser, Company, CompetitorTrend, PricingTier, Email, Outreach, AgentConfig, ToolConfig, AgentLog, ToolLog, AgentTask
from unfold.admin import ModelAdmin
from django.contrib import messages
from django.utils.html import format_html
from django.urls import path, reverse
import subprocess
import os
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from .admins import OutreachAdmin, CompanyAdmin

admin.site.site_header = "Restoring Minds Admin"
admin.site.site_title = "Restoring Minds Admin Portal"
admin.site.index_title = "Welcome to Restoring Minds Admin Portal"

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

""" Competitor Trend Admin """
class CompetitorTrendAdmin(ModelAdmin):
    list_display = ('trend_id', 'date', 'source', 'competitor_name', 'impact_level')
    list_filter = ('impact_level', 'date')
    search_fields = ('trend_description',)


""" Pricing Tier Admin """
class PricingTierAdmin(ModelAdmin):
    list_display = ('min_employees', 'max_employees', 'price', 'features')
    search_fields = ('features',)


""" Agent Config Admin """
class AgentConfigAdmin(ModelAdmin):
    list_display = ('name', 'agent_type', 'is_active', 'created_at')
    list_filter = ('agent_type', 'is_active')
    search_fields = ('name', 'description')


""" Tool Config Admin """
class ToolConfigAdmin(ModelAdmin):
    list_display = ('name', 'tool_type', 'is_active', 'created_at')
    list_filter = ('tool_type', 'is_active')
    search_fields = ('name',)


""" Agent Log Admin """
class AgentLogAdmin(ModelAdmin):
    list_display = ('agent_name', 'status', 'created_at', 'execution_time')
    list_filter = ('status', 'agent_name')
    search_fields = ('agent_name',)


""" Tool Log Admin """
class AgentTaskAdmin(ModelAdmin):
    list_display = ('agent_type', 'status', 'created_at', 'started_at', 'completed_at')
    list_filter = ('status', 'agent_type')
    search_fields = ('agent_type',)

admin.site.register(AgentTask, AgentTaskAdmin)
admin.site.register(AgentLog, AgentLogAdmin)
admin.site.register(ToolConfig, ToolConfigAdmin)
admin.site.register(AgentConfig, AgentConfigAdmin)
admin.site.register(Outreach, OutreachAdmin)
admin.site.register(PricingTier, PricingTierAdmin)
admin.site.register(CompetitorTrend, CompetitorTrendAdmin)
admin.site.register(Company, CompanyAdmin)




