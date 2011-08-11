from armstrong.dev.tasks import *


settings = {
    'DEBUG': True,
    'INSTALLED_APPS': (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'armstrong.apps.crm',
        'armstrong.apps.crm.tests.crm_support',
        'south',
    ),
    'SITE_ID': 1,

    # django-registration settings
    'ACCOUNT_ACTIVATION_DAYS': 100,
}

try:
    import registration
    settings["INSTALLED_APPS"] += ("registration", )
except ImportError:
    pass

main_app = "crm"
full_name = "armstrong.apps.crm"
tested_apps = (main_app,)
