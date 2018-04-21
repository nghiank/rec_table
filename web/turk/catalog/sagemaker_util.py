import os.path
import time

from django.conf import settings
from catalog.constants import *

# Job name will be the same within an hour 
def get_job_name(user_name, original_subset_name):
    timestamp = time.strftime('%Y-%m-%d-%H-7', time.gmtime())
    return  user_name + "-" + original_subset_name.replace("_", "-") + "-" + timestamp + "-job"

# Get the predictor endpoint name
def get_endpoint_name(user_name, subset_name):
    return user_name + '-' + subset_name.replace('_', '-') + "-ep"
