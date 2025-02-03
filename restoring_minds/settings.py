from django.urls import reverse_lazy
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import os

BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'crewai_agents.SiteUser'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-j4652df$+!r3w2-5@-emifnrrskw3w5r(y(z#80&+ue+h$!ief'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['54.205.49.168', '*']


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


# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

"""Define Database Configuration"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL database backend
        'NAME': 'restore_db1',                      # Database name
        'USER': 'jcharles',                         # Database user
        'PASSWORD': '254500',                # Database password
        'HOST': 'localhost',                        # Database host
        'PORT': '5432',                             # Database port
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


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
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
                    {
                        "title": _("Contacts"),
                        "icon": "guardian",
                        "link": reverse_lazy("admin:crewai_agents_contactperson_changelist"),
                    },

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
                     {
                        "title": _("Agents"),
                        "icon": "badge",
                        "link": reverse_lazy("admin:crewai_agents_agent_changelist"),
                    },
                    {
                        "title": _("Tasks"),
                        "icon": "task",
                        "link": reverse_lazy("admin:crewai_agents_task_changelist"),
                    },
                    {
                        "title": _("Tools"),
                        "icon": "construction",
                        "link": reverse_lazy("admin:crewai_agents_tool_changelist"),
                    },
                    {
                        "title": _("Crew"),
                        "icon": "groups_3",
                        "link": reverse_lazy("admin:crewai_agents_crew_changelist"),
                    },
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
