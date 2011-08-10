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
        'south',
    ),
    'SITE_ID': 1,
}

main_app = "crm"
full_name = "armstrong.apps.crm"
tested_apps = (main_app,)
