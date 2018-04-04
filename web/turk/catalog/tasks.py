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
from catalog.path_util import *
from background_task import background
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from pathlib import Path
from django.db import IntegrityError
from django.conf import settings
#from channels import Group
from PIL import Image, ImageFilter


attr = ['num', 'big', 'small', 'roll', 'del']
max_length = [
    4, # 'num': 4,
    3, # 'big': 3,
    3, # 'small': 3,
    1, # 'roll' : 1,
    1, # 'del' : 1
]

    
def get_s3_folder_cells(user_name, id, file_order):
    return os.path.join(user_name, 'cells', str(id), str(file_order) + FILE_EXT)



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
    pass
    #Group('user-' + user_name).send({
    #    "text": json.dumps({
    #        "log": log_message
    #    })
    #})

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
    

@background(schedule=1)
def upload_new_training_record(user_name, train_filename, validation_filename, test_filename):
    #Upload file to S3
    s3_folder = get_s3_folder_bucket_training_data(user_name)
    train_s3 = os.path.join(s3_folder, os.path.split(train_filename)[1])
    validation_s3 = os.path.join(s3_folder, os.path.split(validation_filename)[1])
    test_s3 = os.path.join(s3_folder, os.path.split(test_filename)[1])
    upload_file(train_s3, train_filename)
    print("Uploaded to : " + train_s3)
    upload_file(validation_s3, validation_filename)
    print("Uploaded to : " + validation_s3)
    upload_file(test_s3, test_filename)
    print("Uploaded to : " + test_s3)

    

        


    

    
    
