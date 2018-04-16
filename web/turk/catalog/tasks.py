import boto3
import json
import os
import sagemaker
import shutil
import sys
import time

from PIL import Image, ImageFilter
from background_task import background
from catalog.constants import *
from catalog.data_util import *
from catalog.emnist import *
from catalog.mnist_util import *
from catalog.models import *
from catalog.path_util import *
from catalog.sagemaker_util import *
from catalog.serializers import UserSerializer, GroupSerializer
from catalog.tasks import *
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sagemaker import Session
from sagemaker.tensorflow import TensorFlow
from sagemaker.utils import name_from_image
from shutil import copyfile
from time import gmtime, strftime


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
    
def train_data(
    inputs, role, job_name, instance_type='ml.c4.xlarge', instance_count=1, 
    training_steps=20000, evaluation_steps=100, 
    debug=False, debug_job_name='nghia-2018-04-06-1'):
    mnist_estimator = TensorFlow(#entry_point='/home/0ec2-user/sample-notebooks/sagemaker-python-sdk/tensorflow_distributed_mnist/mnist.py',
                                entry_point='/Users/nghia/rec_table/web/turk/catalog/mnist_sagemaker.py',
                                role=role,
                                training_steps=training_steps, 
                                evaluation_steps=evaluation_steps,
                                train_instance_count=instance_count,
                                train_instance_type=instance_type)
    try:
        if debug:
            print("Trying to attached job_name=" + debug_job_name)
            mnist_estimator = TensorFlow.attach(debug_job_name)
        else:
            print("Trying to create job_name=" + job_name)
            mnist_estimator.fit(inputs, wait = True, job_name=job_name)
    except:
        print("Unexpected error:", sys.exc_info())
        return None
    return mnist_estimator

def create_model(mnist_estimator, instance_type='ml.c4.xlarge'):
    model = mnist_estimator.create_model()
    container_def = model.prepare_container_def(instance_type)
    model_name = name_from_image(container_def['Image'])
    print("Getting model name=" + model_name)
    model.sagemaker_session.create_model(model_name, mnist_estimator.role, container_def)
    return model, model_name

def update_endpoint(model, user_name, production_variant):
    endpoint_name = user_name + "-ep-2"
    client = model.sagemaker_session.sagemaker_client
    response = client.describe_endpoint(EndpointName=endpoint_name)
    print("Response describe_endpoint = " + str(response))
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    endpoint_config_name = user_name + '-endpoint-config-name-' +  timestamp
    if 'EndpointArn' in response:
        #Update existing endpoint
        print('Update existing endpoint ' + endpoint_name + ' with product_variant:' + str(production_variant))
        response = client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name, ProductionVariants=[production_variant])
        print("Create new endpoint config response=" + str(response))
        update_endpoint_response = client.update_endpoint(EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name)
        print("Update endpoint response = " + str(update_endpoint_response))
    else:  
        #Create new endpoint
        print('Create new endpoint '+ endpoint_name + ' with product_variant:' + str(production_variant))
        model.sagemaker_session.endpoint_from_production_variants(endpoint_name, [production_variant], wait=False)

#@background(schedule=1)
def upload_new_training_record(user_name):
    training_image_dir = get_local_train_folder(user_name)
    test_image_dir = training_image_dir
    result_folder = get_mnist_local_folder(user_name)

    # Download default emnist
    download_default_emnist()

    # Convert local images to mnist data
    convert_to_mnist(training_image_dir, test_image_dir, result_folder, ACCEPTED_LABEL) 

    # Convert MNIST Format to TFRecord
    #subset = [2,3,6,7,9]
    origin_subset = ['I', 'K', 'R', 'i', 'k', 'r']
    subset = []
    for character in origin_subset:
        subset.append(char_to_label_index(character))
    print("subset=", subset)
    user_data_sets = read_data_sets(
        result_folder, dtype=dtypes.uint8, subset = subset, validation_size=100)
    emnist_folder = get_emnist_cache_folder()
    default_data_sets = read_data_sets(
        emnist_folder, prefix="emnist-byclass-", dtype=dtypes.uint8, subset=subset, validation_size=5000)

    data_types = ['train', 'validation', 'test']
    data_sets = {}
    for data_type in data_types:
        data_sets[data_type] = merge_data_set(user_data_sets[data_type], default_data_sets[data_type])
        print("data_sets[", data_type, "].images.shape=",data_sets[data_type].images.shape)

    local_tf_record_folder = get_local_tf_record_folder(user_name)
    if os.path.exists(local_tf_record_folder): 
        shutil.rmtree(local_tf_record_folder)
    os.makedirs(local_tf_record_folder)

    train_filename = convert_to(data_sets['train'], 'train', local_tf_record_folder)
    validation_filename = convert_to(data_sets['validation'], 'validation', local_tf_record_folder)
    test_filename = convert_to(data_sets['test'], 'test', local_tf_record_folder)

    return
    #Upload file to S3
    s3_folder = get_s3_folder_bucket_training_data(user_name)
    train_s3 = os.path.join(s3_folder, os.path.split(train_filename)[1])
    validation_s3 = os.path.join(s3_folder, os.path.split(validation_filename)[1])
    test_s3 = os.path.join(s3_folder, os.path.split(test_filename)[1])

    if True:
        print("Start to upload file to S3")
        upload_file(train_s3, train_filename)
        print("Uploaded to : " + train_s3)
        upload_file(validation_s3, validation_filename)
        print("Uploaded to : " + validation_s3)
        upload_file(test_s3, test_filename)
        print("Uploaded to : " + test_s3)
    
    return

    # Setup settings
    print("Start training now for user_name=" + user_name)
    inputs = get_input_training_s3(user_name) 
    print("inputs=" + inputs)
    instance_type =  settings.SAGEMAKER_INSTANCE_TYPE
    initial_instance_count = settings.SAGEMAKER_INITIAL_INSTANCE_COUNT
    role = settings.SAGEMAKER_ROLE
    print("Role = " + role)
    job_name = get_job_name(user_name)
    print("Job name =" + job_name)

    # Train Data
    mnist_estimator = train_data(
        inputs, role, job_name, instance_type = instance_type, training_steps=10000, evaluation_steps=100)
    print("Done with fit for job_name=" + job_name)
    if not mnist_estimator:
        print("Error when executing fit on training data")
        return

    # Create model
    model, model_name = create_model(mnist_estimator, instance_type=instance_type)
    print("Created model name = " + model_name)

    # Update endpoint
    production_variant = sagemaker.production_variant(model_name, instance_type, initial_instance_count)
    update_endpoint(model, user_name, production_variant)
    print("Done with updating endpoint for user_name:" + user_name)