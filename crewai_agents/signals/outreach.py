from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Company, Outreach

@receiver(post_save, sender=Company)
def create_outreach_for_company(sender, instance, created, **kwargs):
    """
    Signal to create an Outreach instance whenever a Company instance is created.
    """
    if created:  
        Outreach.objects.create(
            company=instance, 
            outreach_date=None, 
            message="",  
            message_type='Email',  
            response_status='No Response', 
            follow_up_date=None,  
            comments=None
        )