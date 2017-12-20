import os
import shutil
import json

from shutil import copyfile

from .constants import NROW
from .data_util import read_expected_result
from .mnist_util import convert_to_mnist
from .models import Cell
from .models import ImageSheet
from .models import UserNeuralNet
from .path_util import get_local_output_folder, get_local_output_cells, get_local_train_folder, get_neural_net_data_folder, get_local_test_folder, get_local_train_folder_for_label 
from background_task import background
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from pathlib import Path
from django.db import IntegrityError
from django.conf import settings
from channels import Group
from PIL import Image, ImageFilter


FILE_EXT = '.png'
attr = ['num', 'big', 'small', 'roll', 'del']
max_length = [
    4, # 'num': 4,
    3, # 'big': 3,
    3, # 'small': 3,
    1, # 'roll' : 1,
    1, # 'del' : 1
]
start_index = [1] # We do not care about the first column(order column).
for i in range(0, len(max_length)):
    start_index.append(max_length[i] + start_index[i])
num_col = sum(max_length) + 1

def extract_character(value, index):
    if len(value) <= index or value[index] == ' ':
        return None
    return value[index]

def get_full(v, max_len):
    while len(v) < max_len:
        v = ' ' + v
    return v

def get_file_name(row, col, sub_col, folder):
    if row < (NROW // 2):
        result = (2*num_col) * (row + 1) + start_index[col] + sub_col
    else:
        result = (2*num_col) * (row - 29) + num_col + start_index[col] + sub_col
    return (os.path.join(folder, 'file' + str(result) + FILE_EXT), result)
    
def get_s3_folder_cells(user_name, id, file_order):
    return os.path.join(user_name, 'cells', str(id), str(file_order) + FILE_EXT)


def get_local_new_train_data(user_name, label, id, file_order):
    return os.path.join(get_local_train_folder_for_label(user_name, label), str(id) + '_' + str(file_order) + FILE_EXT)

def write_cell_data(s3_file_name, v, item):
    cell = Cell.objects.update_or_create(
        file_path=s3_file_name,
        expected_char=v,
        image_sheet=item)

def upload_file(s3_file_name, local_file_name):
    file = default_storage.open(s3_file_name, 'w')
    with open(local_file_name, 'rb') as f:
        local_file = File(f)
        for chunk in local_file.chunks():
            file.write(chunk)
    file.close()
    f.close()

def imageprepare(filename, newfilename):
    """
    This function returns the pixel values.
    The imput is a png file location.
    """
    im = Image.open(filename).convert('L')
    width = float(im.size[0])
    height = float(im.size[1])
    newImage = Image.new('L', (28, 28), (0)) #creates white canvas of 28x28 pixels
    if width > height: #check which dimension is bigger
        #Width is bigger. Width becomes 20 pixels.
        nheight = int(round((20.0/width*height),0)) #resize height according to ratio width
        if (nheight == 0): #rare case but minimum is 1 pixel
            nheight = 1
        # resize and sharpen
        img = im.resize((20,nheight), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wtop = int(round(((28 - nheight)/2),0)) #caculate horizontal pozition
        newImage.paste(img, (4, wtop)) #paste resized image on white canvas
    else:
        #Height is bigger. Heigth becomes 20 pixels. 
        nwidth = int(round((20.0/height*width),0)) #resize width according to ratio height
        if (nwidth == 0): #rare case but minimum is 1 pixel
            nwidth = 1
         # resize and sharpen
        img = im.resize((nwidth,20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wleft = int(round(((28 - nwidth)/2),0)) #caculate vertical pozition
        newImage.paste(img, (wleft, 4)) #paste resized image on white canvas
    print("Saveing image " + newfilename)
    newImage.save(newfilename)

@background(schedule=60)
def upload_prediction_images(user_name, id):
    item = ImageSheet.objects.get(pk=id)
    item.state = ImageSheet.PROCESSING
    item.save()
    local_output_folder = get_local_output_folder(user_name, id)
    result, er = read_expected_result(local_output_folder, item)
    print("StartIndex=" + str(start_index))
    local_output_folder_cells = get_local_output_cells(user_name, id)
    files_to_upload = []
    for i in range(0, NROW):
        print("Processing row=" + str(i))
        for j in range(0, len(attr)): # Go through all columns.
            for k in range(0, max_length[j]): # For each digit of each column.
                # Extract label from the expected result firt
                filled_er = get_full(er[i][j], max_length[j])
                v = extract_character(filled_er, k)
                if not v:
                    filled_result = get_full(result[i][j], max_length[j])
                    v = extract_character(filled_result, k)
                # Only upload the file if character is found.
                if v:
                    local_file_name,file_order = get_file_name(i, j, k, local_output_folder_cells)
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
                    copyfile(new_local_file_name, train_file_path)
                    s3_file_name = get_s3_folder_cells(user_name, id, file_order)
                    files_to_upload.append((s3_file_name, new_local_file_name, v))
    print('Uploading files to s3....')
    for file_pair in files_to_upload:
        s3_file_name = file_pair[0]
        local_file_name = file_pair[1]
        expected_char = file_pair[2]
        upload_file(s3_file_name, local_file_name) 
        write_cell_data(s3_file_name, expected_char, item)
    item.state = ImageSheet.PROCESSE2
    item.save()
    print('FINISHED uploading files to s3!')

def copy_neural_net(dest_folder):
    if os.path.exists(dest_folder): 
        shutil.rmtree(dest_folder)
    shutil.copytree(settings.TRAINING_DIR, dest_folder)

def send_log(user_name, log_message):
    Group('user-' + user_name).send({
        "text": json.dumps({
            "log": log_message
        })
    })

#@background(schedule=60)
def training_local_data(user_name):
    print('Process training_local_data:' + user_name)
    neural_net_folder = get_neural_net_data_folder(user_name)
    if not os.path.exists(neural_net_folder):
        os.makedirs(neural_net_folder)
    current_data = UserNeuralNet.objects.filter(username=user_name)
    if not current_data:
        send_log(user_name, 'Copy the default neural net from the system...')
        copy_neural_net(neural_net_folder)
        send_log(user_name, 'DONE Copy the default neural net from the system.')
    else:
        send_log(user_name, 'Download the user neural net from S3...')
        # Download from S3
        send_log(user_name, 'DONE Copy the default neural net from the system.')
    
    training_image_dir = get_local_train_folder(user_name)
    test_image_dir = get_local_test_folder(user_name)

    if os.path.exists(test_image_dir): 
        shutil.rmtree(test_image_dir)
    shutil.copytree(training_image_dir, test_image_dir)

    result_folder = os.path.join(os.path.dirname(test_image_dir), 'mnist')
    accepted_label = '0123456789xXrikRIK' 
    convert_to_mnist(training_image_dir, test_image_dir, result_folder, accepted_label) 
    
    send_log(user_name, 'Save the training-images to MNIST format...')
    send_log(user_name, 'DONE Save the training-images to MNIST format...')
    


    

        


    

    
    
