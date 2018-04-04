
import os
import uuid
import shutil
import subprocess
import logging
import collections

from catalog.constants import ACCEPTED_LABEL
from catalog.data_util import *
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import get_local_output_folder, get_local_output_cells, get_local_train_folder,get_relative_local_train_folder
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
from catalog.path_util import get_local_train_folder

@login_required
def train(request):
    """
    View function for home page of site.
    """
    user_name = request.user.get_username()

    #Get the local folder for the images produced by verify page
    label_img_sorted = get_all_local_data_for_user(user_name)
    return render(
        request,
        'train.html', 
        {
            'username': user_name,
            'label_img': label_img_sorted
        })