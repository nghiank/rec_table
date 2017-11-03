import os
import uuid
import subprocess

from .models import ImageSheet
from django import template
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.shortcuts import render


@login_required
def index(request):
    """
    View function for home page of site.
    """
    imgs = ImageSheet.objects.filter(username__exact=request.user.get_username())
    if request.method == 'POST' and request.FILES['myfile']:
        f = request.FILES['myfile']
        name, extension = os.path.splitext(f.name)
        if extension.upper() not in ['.PNG', '.JPG', '.JPEG']:
            return render(request, 'index.html', {'error':'Invalid image file extension ' + extension})
        file_id = str(uuid.uuid4()) + extension 
        user_name = request.user.get_username()
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
             'items':imgs},
        )

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html', 
        {'items': imgs},
    )

register = template.Library()

@register.filter
def add30(value, arg):
    return value + arg 

@login_required
def verify(request, id):
    """
    Allow user to enter expected value
    """

    # Download file to local folder
    item = ImageSheet.objects.get(pk=id)
    user_name = request.user.get_username()
    file_name = user_name + '/' + item.file_id 
    s3_file = default_storage.open(file_name, 'r')
    local_file = os.path.join('/tmp/', file_name)
    with open('/tmp/'+ file_name, 'wb') as f:
        myfile = File(f)
        myfile.write(s3_file.read())
    myfile.closed
    f.closed    

    # Run the prediction process for the file just downloaded
    print("Local file name :" + local_file)
    result = subprocess.check_output(["./run_prediction.sh", local_file], shell=True)
    #print("Result=" + str(result))


    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'verify.html', {
             'n' : range(1, 31), 
             'item': item,
        },
    )
