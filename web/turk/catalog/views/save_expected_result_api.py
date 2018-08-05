import logging
import os
import shutil
import subprocess
import uuid

from catalog.constants import *
from catalog.data_util import *
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import *
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
from pathlib import Path
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from shutil import copyfile

def move_file_to_training_folder(user_name, id):
    print("Start to move file to training folder...")
    item = ImageSheet.objects.get(pk=id)
    er = ExpectedResult.objects.filter(image_sheet=item)
    result = read_expected_result(er)
    local_output_folder = get_local_output_folder(user_name, id)
    local_output_folder_cells = get_local_output_cells(user_name, id)
    print("Result=" + str(result))
    print("local_output_folder=" + local_output_folder)
    print("local_output_folder_cells=" + local_output_folder_cells)
    files_to_upload = []
    for i in range(0, NROW):
        print("Processing row=" + str(i))
        for j in range(0, len(ATTR)): # Go through all columns.
            for k in range(0, MAX_LENGTH[j]): # For each digit of each column.
                # Extract label from the expected result firt
                filled_er = padding_space(result[i][j], MAX_LENGTH[j])
                v = extract_character(filled_er, k)
                if not v:
                    filled_result = padding_space(result[i][j], MAX_LENGTH[j])
                    v = extract_character(filled_result, k)
                # Only copy the file to training folder if character is found.
                if v:
                    local_file_name,file_order = get_file_name(i, j, k, local_output_folder_cells) 
                    local_file_name = local_file_name + "_final.png"
                    my_file = Path(local_file_name)
                    if not my_file.is_file():
                        print("Path is invalid:" + str(local_file_name))
                        continue
                    train_file_path = get_local_new_train_data(user_name, v, id, file_order)
                    train_folder = get_local_train_folder_for_label(user_name, v)
                    if not os.path.exists(train_folder):
                        os.makedirs(train_folder)
                    new_local_file_name = local_file_name + "_new.png"
                    imageprepare(local_file_name, new_local_file_name)
                    print("Copy file :" + new_local_file_name + " to " + train_file_path)
                    copyfile(new_local_file_name, train_file_path)
    print('FINISHED copied file to training-images!')

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def save_expected_result(request, id):
    """
    API endpoint to save the expected result
    """
    if request.method != 'POST':
        return Response("Error", status=status.HTTP_404_NOT_FOUND)

    print("Save expected result")
    user_name = request.user.get_username()
    order = request.data['order'].split(",")
    num = request.data['num'].split(",")
    big = request.data['big'].split(",")
    small = request.data['small'].split(",")
    roll = request.data['roll'].split(",")
    x = request.data['x'].split(",")
    if (not order or not num or not big or not small or not roll or not x or
        len(order)!= NROW or len(num)!= NROW or len(big)!=NROW or len(small)!=NROW or
        len(roll)!=NROW or len(x)!= NROW) :
        return Response("Save error", status=status.HTTP_200_OK)
    print("Retrieve item..." + str(id))
    item = ImageSheet.objects.get(pk=id)
    try: 
        with transaction.atomic():  
            for i in range(len(order)):
                is_delete = ''
                if x[i] == 'x' or x[i] == 'X':
                    is_delete = 'X'
                row,created = ExpectedResult.objects.update_or_create(
                    image_sheet=item, order=order[i], defaults = {
                        'order': order[i],
                        'num': num[i],
                        'big': big[i],
                        'small': small[i],
                        'roll': roll[i],
                        'is_delete': is_delete
                    })
        # Move file to training image folder
        move_file_to_training_folder(user_name, id)
    except IntegrityError: 
        return Response("Save error", status=status.HTTP_200_OK)

    return Response("Your new characters result are saved - Go to 'Filter' to manually filter wrong images to start training the neuron", status=status.HTTP_200_OK)