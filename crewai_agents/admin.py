from django.contrib import admin
from .models import Agent, Task, Crew, SiteUser, Tool, Company, ContactPerson
from unfold.admin import ModelAdmin

"""Register User Admin Model"""
@admin.register(SiteUser)
class SiteUserAdmin(ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff')

"""Register Agent Admin Model"""
@admin.register(Agent)
class AgentAdmin(ModelAdmin):
    list_display = ('name', 'role', 'goal', 'backstory')
    search_fields = ('name', 'role')  
    list_filter = ('role',)

"""Agent Tool Admin Model"""
@admin.register(Tool)
class ToolAdmin(ModelAdmin):
    list_display = ('name', 'type', 'description') 

"""Register Task Admin Model"""
@admin.register(Task)
class TaskAdmin(ModelAdmin):
    list_display = ('name', 'description', 'assigned_agent')
    search_fields = ('name', 'description')
    list_filter = ('assigned_agent',)

"""Register Crew Admin Model"""
@admin.register(Crew)
class CrewAdmin(ModelAdmin):
    list_display = ('name', 'process', 'verbose')
    filter_horizontal = ('agents', 'tasks')

"""Register Company Admin Model"""
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'industry', 'employee_size', 'location', 'website_url')
    search_fields = ('company_name', 'industry', 'location')
    list_filter = ('industry', 'location')
    list_per_page = 20
    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'employee_size', 'industry', 'location')
        }),
        ('Additional Information', {
            'fields': ('website_url', 'targeting_reason'),
            'classes': ('collapse',) 
        }),
    )

"""Register Contact Person Admin Model"""
@admin.register(ContactPerson)
class ContactPersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'email', 'phone', 'company')
    search_fields = ('name', 'role', 'email', 'company__company_name')
    list_filter = ('role', 'company')
    list_per_page = 20
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'role', 'email', 'phone')
        }),
        ('Company Association', {
            'fields': ('company',),
            'classes': ('collapse',) 
        }),
    )
    
    autocomplete_fields = ['company']