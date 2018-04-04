import logging
import os
import shutil
import subprocess
import uuid

from catalog.emnist import *
from catalog.constants import *
from catalog.data_util import *
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import *
from catalog.serializers import UserSerializer, GroupSerializer
from catalog.mnist_util import *
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import render
from django.utils import timezone
from pathlib import Path
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from shutil import copyfile


@api_view(['POST'])
def add_training_data(request):
    """
    API endpoint to add more training data for logged-in user
    """
    if request.method != 'POST':
        return Response("Error", status=status.HTTP_404_NOT_FOUND)
    print("Add Training Data")

    # Convert local data folder to MNIST format
    user_name = request.user.get_username()
    training_image_dir = get_local_train_folder(user_name)
    test_image_dir = training_image_dir
    result_folder = get_mnist_local_folder(user_name)
    convert_to_mnist(training_image_dir, test_image_dir, result_folder, ACCEPTED_LABEL) 

    # Convert MNIST Format to TFRecord
    subset = [0,1,2,3,4,5,6,7,8,9]
    data_sets = read_data_sets(result_folder, subset = subset)

    local_tf_record_folder = get_local_tf_record_folder(user_name)
    if os.path.exists(local_tf_record_folder): 
        shutil.rmtree(local_tf_record_folder)
    os.makedirs(local_tf_record_folder)

    convert_to(data_sets['train'], 'train', local_tf_record_folder)
    convert_to(data_sets['validation'], 'validation', local_tf_record_folder)
    convert_to(data_sets['test'], 'test', local_tf_record_folder)

    return Response("Training data is added successfully and uploaded to S3 to be wait for retrain", status=status.HTTP_200_OK)