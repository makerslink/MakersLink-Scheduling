"""
Django settings for makerslink project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR_PK_DIR = os.path.abspath(os.path.join(BASE_DIR, "../pks/"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/


if os.getenv('DJANGO_ENV') == 'prod':
    print("Running with production settings.")
    DEBUG = False
    ALLOWED_HOSTS = ['scheduling.makerslink.se', 'vhost.makerslink', 'vhost.makerslink.se', '127.0.0.1']
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECRET_KEY = os.environ.get("DJANGO_SECRET" )
    SITE_URL = 'https://scheduling.makerslink.se'
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # ...
else:
    DEBUG = True
    ALLOWED_HOSTS = ['*']    
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = '!wdai3!c+cs7z!@w=27*b7(ggxi32!uw449=*ji+4m(mp#au+1'
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MENU_EXTRA = [
    {'name':'Hjälp', 'link':'https://docs.google.com/document/d/1ut9KHgJejQpmta0l_Gh0D8yWoMklXmgzCSI5yfROSEA/edit?usp=sharing', 'class':'bg-info text-white font-weight-bold'},
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scheduler.apps.SchedulerConfig',
    'accounts.apps.AccountsConfig',
    'bootstrap4',
    'bootstrap_datepicker_plus',
    #'djangobower',
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

ROOT_URLCONF = 'makerslink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'scheduler.context_processors.extra_menu_processor'
            ],
        },
    },
]

WSGI_APPLICATION = 'makerslink.wsgi.application'

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'makerslink/db/db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Stockholm'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTH_USER_MODEL = "accounts.User"

LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'scheduling@makerslink.se'
EMAIL_HOST_PASSWORD = os.getenv('SCHEDULING_PASS')
EMAIL_USE_TLS = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../static/"))

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'djangobower.finders.BowerFinder',
]

BOOTSTRAP4 = {
    'include_jquery': True,
}

#BOWER_COMPONENTS_ROOT = '//home/bobo/django-apps/makerslink/makerslink/components/'
#BOWER_INSTALLED_APPS = (
#    'jquery',
#    'jquery-ui',
#    'bootstrap'
#)
