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

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
@login_required
def index(request):
    """
    View function for home page of site.
    """
    imgs = ImageSheet.objects.filter(username__exact=request.user.get_username())
    user_name = request.user.get_username()
    if request.method == 'POST' and request.FILES['myfile']:
        f = request.FILES['myfile']
        name, extension = os.path.splitext(f.name)
        if extension.upper() not in ['.PNG', '.JPG', '.JPEG']:
            return render(request, 'index.html', {'error':'Invalid image file extension ' + extension})
        file_id = str(uuid.uuid4()) + extension 
        file_name = user_name + '/' + file_id 
        file = default_storage.open(file_name, 'w')
        for chunk in f.chunks():
            file.write(chunk)
        file.close()
        image_sheet = ImageSheet.objects.create(
            username=user_name,
            file_id=file_id,
            url=default_storage.url(file_name),
            state=ImageSheet.FRESH)
        # Render the HTML template index.html with the data in the context variable
        return render(
            request,
            'index.html',
            {'msg': 'You succesfully uploaded the image:' + file_id,
             'items':imgs, 
             'error': None,
             'username': user_name},
        )

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html', 
        {'items': imgs, 
        'msg': None,
        'error': None,
        'username': user_name},
    )