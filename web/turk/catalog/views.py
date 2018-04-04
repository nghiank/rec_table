import os
import uuid
import shutil
import subprocess
import logging

from .constants import NROW
from .data_util import read_expected_result, read_predicted_result
from .models import ExpectedResult
from .models import ImageSheet
from .path_util import get_local_output_folder, get_local_output_cells, get_local_train_folder
from .serializers import UserSerializer, GroupSerializer
from .tasks import upload_prediction_images, training_local_data
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

def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


