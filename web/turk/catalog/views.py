import os
import uuid
import subprocess

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer

from .models import ImageSheet
from .models import ExpectedResult
from django import template
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

NROW = 60

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

@api_view(['POST'])
def save_expected_result(request, id):
    """
    API endpoint to save the expected result
    """
    if request.method != 'POST':
        return Response("Error", status=status.HTTP_404_NOT_FOUND)

    order = request.data.getlist('order') 
    num = request.data.getlist('num')
    big = request.data.getlist('big')
    small = request.data.getlist('small')
    roll = request.data.getlist('roll')
    x = request.data.getlist('x')
    if (not order or not num or not big or not small or not roll or not x or
        len(order)!= NROW or len(num)!= NROW or len(big)!=NROW or len(small)!=NROW or
        len(roll)!=NROW or len(x)!= NROW) :
        return Response("Save error", status=status.HTTP_200_OK)
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
    except IntegrityError: 
        return Response("Save error", status=status.HTTP_200_OK)
    return Response("Your expected result is saved successfully", status=status.HTTP_200_OK)

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
             'username': user_name},
        )

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html', 
        {'items': imgs, 'username': user_name},
    )



@login_required
def verify(request, id):
    """
    Allow user to enter expected value
    """

    # Download file to local folder
    item = ImageSheet.objects.get(pk=id)
    user_name = request.user.get_username()
    local_output_folder = os.path.join('/tmp', user_name, id)
    file_name = user_name + '/' + item.file_id 
    s3_file = default_storage.open(file_name, 'r')
    local_file = os.path.join(local_output_folder, item.file_id)
    if not os.path.exists(os.path.dirname(local_file)):
        try:
            os.makedirs(os.path.dirname(local_file))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(local_file, 'wb') as f:
        myfile = File(f)
        myfile.write(s3_file.read())
    myfile.closed
    f.closed    

    # Run the prediction process for the file just downloaded
    local_output_folder_cells = os.path.join(local_output_folder, 'cells')
    prediction_path = os.path.join(os.path.dirname(__file__), '../run_prediction.sh')
    result = subprocess.check_output([prediction_path + " " + local_file + " " + local_output_folder_cells], shell=True)
    # The result is written in result.txt
    output_result = os.path.join(local_output_folder, 'result.txt')
    with open(output_result) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    result = [x.split(",") for x in content]
    expected_results = ExpectedResult.objects.filter(image_sheet=item)
    # Render the HTML template index.html with the data in the context variable
    er = []
    for i in range(0,60):
        er.append({})
    for expected_result in expected_results:
        r = int(expected_result.order) - 1
        er[int(expected_result.order) - 1] = [
            expected_result.num,
            expected_result.big,
            expected_result.small,
            expected_result.roll,
            expected_result.is_delete,
        ]
    return render(
        request,
        'verify.html', {
             'n' : range(0, 30), 
             'item': item,
             'result': result,
             'expected_results': er,
             'username': user_name,
        },
    )
