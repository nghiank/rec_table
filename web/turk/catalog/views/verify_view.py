import os
import uuid
import shutil
import subprocess
import logging

from catalog.constants import NROW
from catalog.data_util import read_expected_result, read_predicted_result
from catalog.models import ExpectedResult
from catalog.models import ImageSheet
from catalog.path_util import get_local_output_folder, get_local_output_cells 
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

@login_required
def verify(request, id):
    """
    Allow user to enter expected value
    """
    # Download file to local folder
    item = ImageSheet.objects.get(pk=id)
    user_name = request.user.get_username()
    local_output_folder = get_local_output_folder(user_name, id)
    file_name = user_name + '/' + item.file_id 
    local_file = os.path.join(local_output_folder, item.file_id)
    s3_file = default_storage.open(file_name, 'r')
    print("Local file=" + local_file)
    if not os.path.exists(os.path.dirname(local_file)):
        try:
            os.makedirs(os.path.dirname(local_file))
        except OSError as exc: # Guard against race condition
            print("Exception happening##################################")
            if exc.errno != errno.EEXIST:
                raise
    with open(local_file, 'wb') as f:
        myfile = File(f)
        myfile.write(s3_file.read())
    myfile.closed
    f.closed    
    # Run the prediction process for the file just downloaded
    local_output_folder_cells = get_local_output_cells(user_name, id)
    if os.path.isdir(local_output_folder_cells):
        shutil.rmtree(local_output_folder_cells)
    os.makedirs(local_output_folder_cells)

    prediction_path = os.path.join(os.path.dirname(__file__), '../../run_prediction.sh')
    cmd_activate_tensorflow = "source " + os.path.join(settings.TENSORFLOW_DIR,'tensorflow','bin','activate') 
    cmd = cmd_activate_tensorflow + " && " + prediction_path + " " + local_file + " " + local_output_folder_cells + " " + user_name
    print("Running prediction: " + cmd)
    try:
        result = subprocess.check_output([cmd], shell=True)
    except subprocess.CalledProcessError as e:
        print("Exception happned in the prediction : " + e.output)
    print("Done prediction: " + cmd)
    print("Result from running prediction:", result.decode('ascii'))
    predicted_result = read_predicted_result(local_output_folder)
    expected_results = ExpectedResult.objects.filter(image_sheet=item)
    print("Expected result is read...Time to render")
    expected_result_for_renderering = read_expected_result(expected_results) if expected_results else None
    stored_result_before = True if expected_results else False
    return render(
        request,
        'verify.html', {
            'n' : range(0, 30), 
            'item': item,
            'result': predicted_result,
            'stored_result_before': stored_result_before,
            'expected_results': expected_result_for_renderering,
            'username': user_name,
        })