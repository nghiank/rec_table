import boto3
import logging
import os
import shutil
import subprocess
import uuid

from background_task.models import Task
from catalog.constants import *
from catalog.data_util import *
from catalog.emnist import *
from catalog.mnist_util import *
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import *
from catalog.serializers import UserSerializer, GroupSerializer
from catalog.tasks import *
from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
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
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shutil import copyfile

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_training_data(request):
    """
    API endpoint to add more training data for logged-in user
    """
    if request.method != 'POST':
        return Response("Error", status=status.HTTP_404_NOT_FOUND)
    # Convert local data folder to MNIST format
    user_name = request.user.get_username()

    user_type = ContentType.objects.get_for_model(User)
    print("User_type:" , user_type , "User_id:" , request.user.id)
    existing_task = Task.objects.filter(creator_object_id=request.user.id, creator_content_type_id=user_type)
    if existing_task.count() == 0:
        upload_new_training_record(user_name, creator=request.user, verbose_name='Training Data')
        return Response("Training data task is created successfully and when the task start, it will start to train the neural network", status=status.HTTP_200_OK)
    else:
        return Response("Training data task was already created - you need to try again in few hours", status=status.HTTP_200_OK)
        