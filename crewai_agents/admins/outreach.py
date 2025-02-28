from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

class OutreachAdmin(ModelAdmin):
    list_display = ('company_name', 'get_email_preview', 'status')
    list_display_links =  ('company_name',)
    search_fields = ('company__name', 'comments', 'email__name', 'email__subject', 'email__content')
    list_filter = ('outreach_date', 'status')
    ordering = ('-outreach_date',)
    list_per_page = 10
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'email', 'outreach_date', 'status')
        }),
        ('Email Preview', {
            'fields': ('get_email_content',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('comments',)
        })
    )

    readonly_fields = ('get_email_content',)

    def company_name(self, obj):
        return obj.company.company_name if obj.company else '-'
    company_name.admin_order_field = 'company__name'
    company_name.short_description = 'Company'

    def get_email_preview(self, obj):
        if obj.email:
            return format_html(
                '<div style="max-width: 300px;">'
                '<strong style="display: block; margin-bottom: 5px;">{}</strong>'
                '<div style="color: #666; font-size: 0.9em;">{}</div>'
                '</div>',
                obj.email.subject,
                (obj.email.content[:100] + '...') if len(obj.email.content) > 100 else obj.email.content
            )
        return '-'
    get_email_preview.admin_order_field = 'email__subject'
    get_email_preview.short_description = 'Email Preview'

    def get_email_content(self, obj):
        if obj.email:
            return format_html(
                '<div style="max-width: 600px; padding: 20px; border: 1px solid #ddd; border-radius: 4px;">'
                '<div style="border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">'
                '<strong style="font-size: 1.1em;">Template:</strong> {}<br>'
                '<strong style="font-size: 1.1em;">Recipient:</strong> {}<br>'
                '<strong style="font-size: 1.1em;">Subject:</strong> {}'
                '</div>'
                '<div style="white-space: pre-wrap; font-family: Arial, sans-serif;">{}</div>'
                '<div style="margin-top: 10px; font-size: 0.9em; color: #666;">'
                '</div>'
                '</div>',
                obj.email.name,
                obj.email.recipient,
                obj.email.subject,
                obj.email.content
            )
        return '-'
    get_email_content.short_description = 'Email Content'

    def get_comments(self, obj):
        if obj.comments:
            return format_html(
                '<span title="{}" style="color: #666;">{}</span>', 
                obj.comments, 
                (obj.comments[:50] + '...') if len(obj.comments) > 50 else obj.comments
            )
        return '-'
    get_comments.short_description = 'Comments'

    class Media:
        css = {
            'all': ['admin/css/email_preview.css']
        }