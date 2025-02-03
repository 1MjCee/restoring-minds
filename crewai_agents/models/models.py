from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError


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
    
"""Tool Model"""
class Tool(models.Model):
    name = models.CharField(max_length=255)  
    type = models.CharField(max_length=255)  
    description = models.TextField(default="")

    def __str__(self):
        return self.name

"""Agent Model"""
class Agent(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    goal = models.TextField(default="")
    backstory = models.TextField(default="")
    tools = models.ManyToManyField(Tool, related_name='agents')
    verbose = models.BooleanField(default=False)
    memory = models.BooleanField(default=False)
    llm = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

"""Task Model"""
class Task(models.Model):
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    expected_output = models.TextField(default="")
    context = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_tasks')
    assigned_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['order']
    
"""Crew Model"""
class Crew(models.Model):
    name = models.CharField(max_length=255)
    agents = models.ManyToManyField(Agent, related_name='crews')
    tasks = models.ManyToManyField(Task, related_name='crews')
    process = models.CharField(max_length=50, default="sequential")
    verbose = models.BooleanField(default=False)

    def __str__(self):
        return self.name

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
    
"""Contact Person Model"""
class ContactPerson(models.Model):
    CONTACT_METHODS = [
        ('Email', 'Email'),
        ('Phone', 'Phone'),
        ('LinkedIn', 'LinkedIn'),
    ]
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')
    role = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    preferred_contact_method = models.CharField(max_length=50, choices=CONTACT_METHODS, default='Email')
    last_contact_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

"""Outreach Model"""
class Outreach(models.Model):
    OUTREACH_METHODS = [
        ('Email', 'Email'),
        ('LinkedIn', 'LinkedIn Message'),
        ('Phone', 'Phone Call'),
    ]

    RESPONSE_STATUSES = [
        ('awaiting', 'Awaiting Response'),
        ('Interested', 'Interested'),
        ('No Response', 'No Response'),
        ('Not Interested', 'Not Interested'),
    ]

    outreach_id = models.AutoField(primary_key=True)
    company = models.OneToOneField(Company, on_delete=models.CASCADE, blank=True, null=True, related_name='outreach_company')
    outreach_date = models.DateField(null=True, blank=True, default=None)
    message = models.TextField(blank=True, null=True, default="")  
    message_type = models.CharField(max_length=50, choices=OUTREACH_METHODS, default='Email')
    response_status = models.CharField(max_length=50, choices=RESPONSE_STATUSES, default='No Response')
    follow_up_date = models.DateField(blank=True, null=True, default=None)
    comments = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return f"Outreach {self.outreach_id} to {self.company}"

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

