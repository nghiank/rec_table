import os
import uuid
import shutil
import subprocess
import logging

from catalog.constants import NROW
from catalog.data_util import read_expected_result, read_predicted_result
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import get_local_output_folder, get_local_output_cells, get_local_train_folder
from catalog.serializers import UserSerializer, GroupSerializer
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
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def remove_image(request, id):
    """
    API endpoint to remove local image
    """
    if request.method != 'POST':
        return Response("Error", status=status.HTTP_404_NOT_FOUND)
    # Launch task to upload single character image into S3
    user_name = request.user.get_username()
    prefix = "/media/"
    id = id[len(prefix):]
    full_path = os.path.join(settings.TMP_DIR, id)
    print("Removing image : " + full_path)
    os.remove(full_path)
    return Response("Image removed successfully", status=status.HTTP_200_OK)