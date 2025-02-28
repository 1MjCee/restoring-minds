from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

class CompanyAdmin(ModelAdmin):
    list_display = ('company_name', 'employee_size', 'industry', 'location', 
                   'website_url', 'priority_score', 'get_decision_makers_display')
    search_fields = ('company_name', 'industry', 'location')
    list_filter = ('industry', 'location')
    ordering = ('company_name',)
    list_per_page = 10

    def get_decision_makers_display(self, obj):
        """Format decision makers as an HTML list"""
        if not obj.decision_makers: 
            return "No decision makers"
            
        dm_list = []
        for dm in obj.decision_makers: 
            dm_info = [
                f"<strong>{dm.get('name', 'N/A')}</strong>",
                f"Role: {dm.get('role', 'N/A')}",
                f"Email: {dm.get('email', 'N/A')}",
                f"Phone: {dm.get('phone', 'N/A')}"
            ]
            dm_list.append(" | ".join(dm_info))
            
        return format_html("<br>".join(dm_list))
    
    get_decision_makers_display.short_description = "Decision Makers"