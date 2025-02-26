from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from ..models import Company, Outreach, Email

@receiver(post_save, sender=Company)
def create_outreach_for_company(sender, instance, created, **kwargs):
    """
    Signal to create an Outreach instance whenever a Company instance is created.
    Optionally sets up default email template and scheduled outreach date.
    """
    if created:
        template = Email.objects.filter(is_default=True).first()
        
        default_outreach_date = timezone.now().date() + timezone.timedelta(days=7)
        
        Outreach.objects.create(
            company=instance,
            status='pending',
            email=template, 
            outreach_date=default_outreach_date,
            comments=f"Auto-generated outreach for {instance.company_name}"
        )