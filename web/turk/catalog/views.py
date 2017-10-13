import os
import uuid

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.shortcuts import render
from .models import ImageSheet


@login_required
def index(request):
    """
    View function for home page of site.
    """
    if request.method == 'POST' and request.FILES['myfile']:
        f = request.FILES['myfile']
        name, extension = os.path.splitext(f.name)
        if extension not in ['.png', '.jpg', 'jpeg']:
            return render(request, 'index.html', {'error':'Invalid image file'})
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
            state=ImageSheet.FRESH)

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
    )