import os
from .base import *

# Training settings
TMP_DIR='/Users/nghia/tmp'
TENSORFLOW_DIR='/Users/nghia/tmp'
TRAINING_DIR = '/Users/nghia/rec_table/train/checkpoint'
TRAINING_DATA_BUCKET = "training-data-dev"

# Sagemakger setting
SAGEMAKER_INITIAL_INSTANCE_COUNT = 1
SAGEMAKER_ROLE = 'arn:aws:iam::497017843977:role/service-role/AmazonSageMaker-ExecutionRole-20180322T225994'
SAGEMAKER_INSTANCE_TYPE = 'ml.c4.xlarge'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'nghia',
        'USER': 'turk_user',
        'PASSWORD': 'dev-test-123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}