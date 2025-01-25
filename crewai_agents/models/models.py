from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    expected_output = models.TextField(default="")
    assigned_agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return self.name
    
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
    targeting_reason = models.TextField()

    def __str__(self):
        return self.company_name
    
"""Contact Person Model"""
class ContactPerson(models.Model):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='contacts')

    def __str__(self):
        return self.name