import os
from .base import *
from os.path import expanduser

# Training settings
TMP_DIR='/home/ubuntu/tmp'
TENSORFLOW_DIR='/home/ubuntu/tmp'
DEBUG_LOG_DIR = '/var/log/app_logs'
TRAINING_DIR = '/home/ubuntu/rec_table/train/checkpoint'
TRAINING_DATA_BUCKET = "training-data-prod"

# Sagemaker settings
SAGEMAKER_INITIAL_INSTANCE_COUNT = 1
SAGEMAKER_ROLE = 'arn:aws:iam::497017843977:role/service-role/AmazonSageMaker-ExecutionRole-20180322T225994'
SAGEMAKER_INSTANCE_TYPE = 'ml.c4.xlarge'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'logging.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': DEBUG_LOG_DIR + "/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'turk': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
        'catalog.views.verify_view': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['/home/ubuntu/rec_table/web/turk/templates'],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'turk.wsgi.application'
# Database
# brew install postgresm/en/1.11/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

ALLOWED_HOSTS = [
    'ec2-54-165-20-212.compute-1.amazonaws.com',
]