"""
Django settings for synergycrm project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&vnt5=f*)&3u4=($f@fm#60v82q^p)*%*^t7e)xznok(#8nmq4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

if DEBUG:
	ALLOWED_HOSTS.append('localhost')
	ALLOWED_HOSTS.append('127.0.0.1')
else:
	ALLOWED_HOSTS.append('test.sngy.ru')
	ALLOWED_HOSTS.append('office.sngy.ru')

# Application definition

INSTALLED_APPS = [
	'django.contrib.auth',
	'django.contrib.admin',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.postgres',
	'crm.apps.CrmConfig',
	'graphene_django',
	'companies.apps.CompaniesConfig',
	'users.apps.UsersConfig',
	'reports.apps.ReportsConfig',
	'projects.apps.ProjectsConfig',
	'absences.apps.AbsencesConfig',
	'salary.apps.SalaryConfig',
	'menu.apps.MenuConfig',
	'help.apps.HelpConfig',
	'warehouse.apps.WarehouseConfig',
	'tasks.apps.TasksConfig',
	'documents.apps.DocumentsConfig',
	'clients.apps.ClientsConfig',
	'notice.apps.NoticeConfig',
	'project_specifications.apps.ProjectSpecificationsConfig',
	'comments.apps.CommentsConfig',
	'project_logging.apps.ProjectLoggingConfig',
	'logistics.apps.LogisticsConfig'
]

if DEBUG:
	INSTALLED_APPS.append('corsheaders')

CORS_ORIGIN_WHITELIST = ('localhost:8080', '127.0.0.1:8080')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = default_headers + ('cache-control',)

CSRF_TRUSTED_ORIGINS = ['localhost:8080', ]

if not DEBUG:
	del CORS_ORIGIN_WHITELIST
	del CORS_ALLOW_CREDENTIALS
	del CORS_ALLOW_HEADERS
	del CSRF_TRUSTED_ORIGINS

MIDDLEWARE = [
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django_currentuser.middleware.ThreadLocalUserMiddleware',
	'synergycrm.middleware.IfBatchIsTrueWhenUploadFile',
]

if DEBUG:
	MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

ROOT_URLCONF = 'synergycrm.urls'

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

WSGI_APPLICATION = 'synergycrm.wsgi.application'

GRAPHENE = {
	'SCHEMA': 'crm.api.schema',
	'MIDDLEWARE': [
		'crm.api.AuthorizationMiddleware'
	]
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'postgres',
		'USER': 'username',
		'PASSWORD': 'password',
		'HOST': 'db',
		'PORT': '5432'
	}
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Volgograd'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/ver2/static/'

MEDIA_URL = '/media/'

if DEBUG:
	MEDIA_ROOT = 'D://downloads/'
else:
	MEDIA_ROOT = '/var/www/ver2/media/'

# Куки
SESSION_COOKIE_AGE = 3600 * 12  # Кука сессии живет 12 часов

# Настройки отправки почты
EMAIL_HOST = 'smtp.yandex.com'
EMAIL_HOST_USER = 'report@sngy.ru'
EMAIL_HOST_PASSWORD = 'z5c44un8YQ'
EMAIL_USE_TLS = True

# Путь до директории с папками от проектов
PROJECTS_DIR = '/mnt/smb/!Проекты/'
