
import os
import uuid
import shutil
import subprocess
import logging
import collections

from catalog.constants import ACCEPTED_LABEL
from catalog.data_util import read_expected_result, read_predicted_result
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
    local_image_folder = get_local_train_folder(user_name)
    print("Local folder = " + local_image_folder)
    label_img = {}
    for label in os.listdir(local_image_folder): 
        if label not in ACCEPTED_LABEL:
            continue
        dirname = os.path.join(local_image_folder, label)
        print("Label name = " + dirname)
        for file in os.listdir(dirname):
            _, extension = os.path.splitext(file)
            if extension not in [".png", ".jpg", "jpeg"]:
                continue
            if label not in label_img:
                label_img[label] = []
            full_path = os.path.join(get_relative_local_train_folder(user_name), label, file)
            full_path = os.path.join('/media', full_path)
            label_img[label].append(full_path)

    print("Getting data in local folder " + dirname)
    label_img_sorted = collections.OrderedDict(sorted(label_img.items()))
    return render(
        request,
        'train.html', 
        {
            'username': user_name,
            'label_img': label_img_sorted
        })