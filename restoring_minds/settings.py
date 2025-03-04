from django.urls import reverse_lazy
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv
import os
from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'crewai_agents.SiteUser'

load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-j4652df$+!r3w2-5@-emifnrrskw3w5r(y(z#80&+ue+h$!ief'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['jacquelinecampbellai.com', '*', '127.0.0.1']

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    "market_researcher_daily": {
        "task": "myapp.tasks.run_market_researcher_scheduled",
        "schedule": crontab(hour=8, minute=0),
    },
    "business_researcher_daily": {
        "task": "myapp.tasks.run_business_researcher_scheduled",
        "schedule": crontab(hour=8, minute=0),
    },
    "decision_maker_daily": {
        "task": "myapp.tasks.run_decision_maker_scheduled",
        "schedule": crontab(hour=8, minute=0),
    },
    "outreach_specialist_daily": {
        "task": "myapp.tasks.run_outreach_specialist_scheduled",
        "schedule": crontab(hour=8, minute=0),
    },
}

# Application definition
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters", 
    "unfold.contrib.forms",  
    "unfold.contrib.inlines",  
    "unfold.contrib.import_export",
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crewai_agents',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restoring_minds.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restoring_minds.wsgi.application'


"""Define Database Configuration"""
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql', 
#         'NAME': 'restoring_db',                     
#         'USER': 'jcharles',                        
#         'PASSWORD': '254500',               
#         'HOST': 'localhost',                       
#         'PORT': '5432',                             
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'  
STATICFILES_DIRS = [  
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

UNFOLD = {
    "SITE_TITLE": "Restoring Minds",
    "SITE_HEADER": "Admin Panel",
    "SITE_URL": "/",
    
    "SITE_SYMBOL": "speed",  
    
    "SHOW_VIEW_ON_SITE": False, 
    "DASHBOARD_CALLBACK": "restoring_minds.views.dashboard_callback",
    "SHOW_HISTORY": True,
    
    "COLORS": {
        "font": {
            "subtle-light": "107 114 128",
            "subtle-dark": "156 163 175",
            "default-light": "75 85 99",
            "default-dark": "209 213 219",
            "important-light": "17 24 39",
            "important-dark": "243 244 246",
        },
        "primary": {
            "50": "250 245 255",
            "100": "243 232 255",
            "200": "233 213 255",
            "300": "216 180 254",
            "400": "192 132 252",
            "500": "168 85 247",
            "600": "147 51 234",
            "700": "126 34 206",
            "800": "107 33 168",
            "900": "88 28 135",
            "950": "59 7 100",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "nl": "🇧🇪",
            },
        },
    },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": False,
        
        "navigation": [
            {
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
            {
                "title": _("Data Management"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Outreach"),
                        "icon": "mark_email_unread",
                        "link": reverse_lazy("admin:crewai_agents_outreach_changelist"),
                    },
                     {
                        "title": _("Companies"),
                        "icon": "add_business",
                        "link": reverse_lazy("admin:crewai_agents_company_changelist"),
                    },
                    # {
                    #     "title": _("Emails"),
                    #     "icon": "guardian",
                    #     "link": reverse_lazy("admin:crewai_agents_email_changelist"),
                    # },

                ],
            },
            {
                "title": _("Analytics & Insights"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Pricing"),
                        "icon": "price_check",
                        "link": reverse_lazy("admin:crewai_agents_pricingtier_changelist"),
                    },
                    {
                        "title": _("Market Trends"),
                        "icon": "trending_up",
                        "link": reverse_lazy("admin:crewai_agents_competitortrend_changelist"),
                    },
                ],
            },
             {
                "title": _("Core AI Components"),
                "separator": True,
                "collapsible": False,
                "items": [
                    #  {
                    #     "title": _("Agents"),
                    #     "icon": "badge",
                    #     "link": reverse_lazy("admin:crewai_agents_agent_changelist"),
                    # },
                    # {
                    #     "title": _("Tasks"),
                    #     "icon": "task",
                    #     "link": reverse_lazy("admin:crewai_agents_task_changelist"),
                    # },
                    # {
                    #     "title": _("Tools"),
                    #     "icon": "construction",
                    #     "link": reverse_lazy("admin:crewai_agents_tool_changelist"),
                    # },
                    # {
                    #     "title": _("Crew"),
                    #     "icon": "groups_3",
                    #     "link": reverse_lazy("admin:crewai_agents_crew_changelist"),
                    # },
                ],
            },
             {
                "title": _("System Settings"),
                "separator": True,
                "collapsible": False,
                "items": [
                     {
                        "title": _("Users"),
                        "icon": "manage_accounts",
                        "link": reverse_lazy("admin:crewai_agents_siteuser_changelist"),
                    },
                ],
            },
        ],
    },
}


CREW_PROCESS_FILE = os.path.join(BASE_DIR, 'crew_processes.json')
