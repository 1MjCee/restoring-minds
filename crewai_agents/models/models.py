from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
import uuid


"""Admin User Manager"""
class SiteUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)

"""User Model"""
class SiteUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Add unique related_name attributes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="crewai_agents_user_groups", 
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
        related_name="crewai_agents_user_permissions",
        related_query_name="user",
    )

    objects = SiteUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email
    

"""Company Model"""
class Company(models.Model):
    company_name = models.CharField(max_length=255)
    employee_size = models.IntegerField()
    industry = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    website_url = models.URLField()
    revenue_growth = models.FloatField(blank=True, null=True)
    stress_level_score = models.IntegerField(blank=True, null=True)
    wellness_culture_score = models.IntegerField(blank=True, null=True)
    priority_score = models.FloatField(blank=True, null=True)
    last_updated = models.DateField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    targeting_reason = models.TextField()

    # Contact Persons (stored as JSON)
    decision_makers = models.JSONField(default=list, blank=True, help_text="""
        List of contact persons in format:
        [
            {
                "name": "string",
                "role": "string",
                "email": "email@example.com",
                "phone": "string",
                "linkedin_profile": "url",
                "preferred_contact": "Email|Phone|LinkedIn",
                "last_contact_date": "YYYY-MM-DD",
                "notes": "string"
            }
        ]
    """)

    def __str__(self):
        return self.company_name
    
    def get_pricing_tier(self):
        """
        Returns the pricing tier for the company based on its employee size.
        """
        try:
            return PricingTier.objects.filter(
                min_employees__lte=self.employee_size,
                max_employees__gte=self.employee_size
            ).first()
        except PricingTier.DoesNotExist:
            return None
    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


"""CompetitorTrend Model"""
class CompetitorTrend(models.Model):
    IMPACT_LEVELS = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    trend_id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=200)
    trend_description = models.TextField(default="")
    competitor_name = models.CharField(max_length=100, blank=True, null=True)
    impact_level = models.CharField(max_length=50, choices=IMPACT_LEVELS)
    notes = models.TextField(default="")

    def __str__(self):
        return f"Trend {self.trend_id} - {self.trend_description[:50]}"


"""PricingTier Model"""
class PricingTier(models.Model):
    min_employees = models.IntegerField(help_text="Minimum number of employees for this tier.")
    max_employees = models.IntegerField(help_text="Maximum number of employees for this tier.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price for this tier.")
    features = models.TextField(blank=True, null=True, help_text="Features included in this tier.")

    def __str__(self):
        return f"Tier for {self.min_employees}-{self.max_employees} employees - ${self.price}"

    def clean(self):
        """
        Validate that the min_employees is less than max_employees.
        Also ensure that the employee ranges do not overlap with existing tiers.
        """
        if self.min_employees >= self.max_employees:
            raise ValidationError("min_employees must be less than max_employees.")

        # Check for overlapping employee ranges
        overlapping_tiers = PricingTier.objects.filter(
            min_employees__lte=self.max_employees,
            max_employees__gte=self.min_employees
        ).exclude(pk=self.pk)  

        if overlapping_tiers.exists():
            raise ValidationError("This employee range overlaps with an existing tier.")

    def save(self, *args, **kwargs):
        """
        Override the save method to enforce a maximum of 3 pricing tiers.
        """
        if PricingTier.objects.count() >= 3 and not self.pk:
            raise ValidationError("Only 3 pricing tiers are allowed.")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['min_employees']

"""EmailTemplate Model"""
class Email(models.Model):
    name = models.CharField(max_length=100)
    recipient = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_default = models.BooleanField(default=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} ({self.subject})"


"""Outreach Model"""
class Outreach(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('updated', 'Updated'),
        ('sent', 'Email Sent'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ]
    outreach_id = models.AutoField(primary_key=True)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, null=True, related_name='outreach_company')
    email = models.ForeignKey(Email, on_delete=models.SET_NULL, blank=True, null=True, related_name='outreach_email')
    outreach_date = models.DateField(null=True, blank=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    comments = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return f"Outreach {self.outreach_id} to {self.company}"
    

# =======================================
# AI PROSPECTING AGENT SYSTEM MODELS
# =======================================

"""AgentConfig Model"""
class AgentConfig(models.Model):
    """Model for storing agent configurations."""
    
    AGENT_TYPES = [
        ('market_researcher', 'Market Researcher'),
        ('business_researcher', 'Business Researcher'),
        ('decision_maker_identifier', 'Decision Maker Identifier'),
        ('outreach_specialist', 'Outreach Specialist'),
    ]
    
    name = models.CharField(max_length=100)
    agent_type = models.CharField(max_length=50, choices=AGENT_TYPES)
    description = models.TextField()
    model_name = models.CharField(max_length=50, default='gpt-4')
    temperature = models.FloatField(default=0.5)
    system_prompt = models.TextField()
    tools = models.JSONField(default=list, help_text="List of tool names this agent can use")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.agent_type})"
    
    class Meta:
        verbose_name = "Agent Configuration"
        verbose_name_plural = "Agent Configurations"

"""ToolConfig Model"""
class ToolConfig(models.Model):
    """Model for storing tool configurations."""
    
    TOOL_TYPES = [
        ('database', 'Database Tool'),
        ('search', 'Search Tool'),
        ('browser', 'Browser Tool'),
        ('email', 'Email Tool'),
        ('analysis', 'Analysis Tool'),
        ('memory', 'Memory Tool'),
    ]
    
    name = models.CharField(max_length=100)
    tool_type = models.CharField(max_length=50, choices=TOOL_TYPES)
    description = models.TextField()
    configuration = models.JSONField(default=dict, help_text="Configuration parameters for the tool")
    rate_limit = models.IntegerField(default=0, help_text="Rate limit in requests per minute (0 for unlimited)")
    requires_auth = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.tool_type})"
    
    class Meta:
        verbose_name = "Tool Configuration"
        verbose_name_plural = "Tool Configurations"

"""AgentLog Model"""
class AgentLog(models.Model):
    """Model for storing agent execution logs."""
    
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=100)
    input_text = models.TextField()
    output_text = models.TextField(blank=True, null=True)
    intermediate_steps = models.JSONField(default=list, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    execution_time = models.FloatField(blank=True, null=True, help_text="Execution time in seconds")
    token_usage = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.agent_name} Log - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name = "Agent Log"
        verbose_name_plural = "Agent Logs"
        ordering = ['-created_at']

"""ToolLog Model"""
class ToolLog(models.Model):
    """Model for storing tool usage logs."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tool_name = models.CharField(max_length=100)
    called_at = models.DateTimeField(auto_now_add=True)
    input_data = models.JSONField(default=dict, blank=True, null=True)
    output_data = models.JSONField(default=dict, blank=True, null=True)
    execution_time = models.FloatField(blank=True, null=True, help_text="Execution time in seconds")
    error_message = models.TextField(blank=True, null=True)
    agent_log = models.ForeignKey(AgentLog, on_delete=models.CASCADE, related_name='tool_logs', blank=True, null=True)
    
    def __str__(self):
        return f"{self.tool_name} Usage - {self.called_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name = "Tool Log"
        verbose_name_plural = "Tool Logs"
        ordering = ['-called_at']

"""AgentTask Model"""
class AgentTask(models.Model):
    """Model for storing asynchronous agent tasks."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    agent_type = models.CharField(max_length=50)
    input_text = models.TextField()
    context_data = models.JSONField(default=dict, blank=True, null=True)
    result_data = models.JSONField(default=dict, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    celery_task_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(SiteUser, on_delete=models.SET_NULL, related_name='agent_tasks', blank=True, null=True)
    
    def __str__(self):
        return f"{self.agent_type} Task - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    class Meta:
        verbose_name = "Agent Task"
        verbose_name_plural = "Agent Tasks"
        ordering = ['-created_at']
    
    def cancel(self):
        """Cancel the task if it's not completed yet."""
        from celery.task.control import revoke
        
        if self.status in ['PENDING', 'RUNNING'] and self.celery_task_id:
            revoke(self.celery_task_id, terminate=True)
            self.status = 'CANCELLED'
            self.save()
            return True
        return False
    
    def get_task_duration(self):
        """Get the duration of the task in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_active(self):
        """Check if the task is currently active."""
        return self.status in ['PENDING', 'RUNNING']

