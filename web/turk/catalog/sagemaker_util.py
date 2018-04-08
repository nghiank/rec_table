import os.path
import time

from django.conf import settings
from catalog.constants import *


# Job name will be the same within an hour 
def get_job_name(user_name):
    timestamp = time.strftime('-%Y-%m-%d-%H-1', time.gmtime())
    return  user_name + timestamp + "-job"

def get_input_training_s3(user_name):
   """
    Return as : "s3://imagesheet1/training-data-dev/nghia/mnist"
   """
   path = "s3://" + settings.AWS_STORAGE_BUCKET_NAME
   path += "/" + settings.TRAINING_DATA_BUCKET
   path += "/" + user_name
   path += "/mnist"
   return path

