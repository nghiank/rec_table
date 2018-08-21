import boto3
import json
import re
import os
import shutil
import sys
import time
import boto3
import botocore
import tensorflow as tf
from PIL import Image, ImageFilter
from background_task import background
from catalog.email_util import *
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
#from sagemaker import Session
#from sagemaker.tensorflow import TensorFlow
#from sagemaker.utils import name_from_image
from shutil import copyfile
from time import gmtime, strftime

# upload, create_training_job, create_endpoint
ENABLE_STAGE = False
STAGE_UPLOAD = "upload"
STAGE_JOB = "create_training_job"
STAGE_CREATE_ENDPOINT = "create_endpoint"
STAGE = STAGE_UPLOAD

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


def send_log(user_name, log_message):
    pass
    #Group('user-' + user_name).send({
    #    "text": json.dumps({
    #        "log": log_message
    #    })
    #})

def get_tensorflow_(
    role, len_subset, checkpoint_path, 
    training_steps=20000, 
    evaluation_steps=100, 
    instance_type='ml.c4.xlarge', 
    instance_count=1):
    mnist_estimator = TensorFlow(
                                entry_point='/Users/nghia/rec_table/web/turk/catalog/mnist_sagemaker.py',
                                role=role,
                                checkpoint_path = checkpoint_path,
                                #train_max_run = 10 * 60,  # Let it run 10mins only
                                training_steps=training_steps, 
                                evaluation_steps=evaluation_steps,
                                train_instance_count=instance_count,
                                train_instance_type=instance_type,
                                hyperparameters = {
                                 'len_subset': len_subset
                                })
    return mnist_estimator

def prepare_checkpoint_(origin_subset_name, user_name):
    user_checkpoint_path = get_user_checkpoint(user_name, origin_subset_name)
    if check_s3_exist(user_checkpoint_path):
        print('Path :', user_checkpoint_path, ' exists')
        return
    common_checkpoint_path = get_user_checkpoint(DEFAULT_USERNAME, origin_subset_name)
    copy_s3_folder(common_checkpoint_path, user_checkpoint_path)
    print("Done with copy the ", common_checkpoint_path, " ===> ", user_checkpoint_path)

    
def train_data_(
    inputs, role, job_name, len_subset, checkpoint_path, instance_type='ml.c4.xlarge', instance_count=1, 
    training_steps=20000, evaluation_steps=100, 
    debug=False, debug_job_name='nghia-2018-04-06-1'):

    mnist_estimator = get_tensorflow_(
        role, len_subset, checkpoint_path, training_steps, evaluation_steps, instance_type, instance_count)
#    try:
    if ENABLE_STAGE and STAGE == STAGE_JOB:
        print("Trying to create job_name ENABLE_STAGE=" + job_name)
        mnist_estimator.fit(inputs, wait = True, job_name=job_name)
        return mnist_estimator
    if debug:
        print("Trying to attached job_name=" + debug_job_name)
        mnist_estimator = TensorFlow.attach(debug_job_name)
        return mnist_estimator
    if ENABLE_STAGE and STAGE == STAGE_CREATE_ENDPOINT:
        print("Trying to attached job_name=" + debug_job_name)
        mnist_estimator = TensorFlow.attach(job_name)
        return mnist_estimator
    print("Trying to create job_name=" + job_name)
    mnist_estimator.fit(inputs, wait = True, job_name=job_name)
#    except:
#        print("Unexpected error:", sys.exc_info())
#        return None
    return mnist_estimator

def create_model(mnist_estimator, instance_type='ml.c4.xlarge'):
    model = mnist_estimator.create_model()
    container_def = model.prepare_container_def(instance_type)
    model_name = name_from_image(container_def['Image'])
    print("Getting model name=" + model_name)
    model.sagemaker_session.create_model(model_name, mnist_estimator.role, container_def)
    return model, model_name

@background(schedule=60)
def update_endpoint_task(job_name, model_name, user_name, origin_subset_name):
    instance_type =  settings.SAGEMAKER_INSTANCE_TYPE
    initial_instance_count = settings.SAGEMAKER_INITIAL_INSTANCE_COUNT
    production_variant = sagemaker.production_variant(
        model_name, instance_type, 
        initial_instance_count, 
        variant_name=origin_subset_name.replace('_','-'))

    print("Attempt to attach existing job_name:", job_name)
    mnist_estimator = TensorFlow.attach(job_name)
    model = mnist_estimator.create_model()
    print("Attempt to update endpoint...")
    update_endpoint(job_name, model, model_name, user_name, origin_subset_name)
    print("Done update endpoint")

def update_endpoint(job_name, model, model_name, user_name, origin_subset_name):
    instance_type =  settings.SAGEMAKER_INSTANCE_TYPE
    initial_instance_count = settings.SAGEMAKER_INITIAL_INSTANCE_COUNT

    production_variant = sagemaker.production_variant(
        model_name, instance_type, 
        initial_instance_count)

    endpoint_name = get_endpoint_name(user_name, origin_subset_name)
    client = model.sagemaker_session.sagemaker_client
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    try:
        response = client.describe_endpoint(EndpointName=endpoint_name)
        print("Response describe_endpoint = " + str(response))
    except:
        response = {}
    endpoint_config_name = user_name + '-endpoint-config-name-' +  timestamp
    if 'EndpointArn' in response:
        if response['EndpointStatus'] != 'InService':
            update_endpoint_task(job_name, model_name, user_name, origin_subset_name)
            return
        #Update existing endpoint
        print('Update existing endpoint ', endpoint_name, ' with product_variant:', production_variant)
        response = client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name, ProductionVariants=[production_variant])
        print("Create new endpoint config response=" + str(response))
        update_endpoint_response = client.update_endpoint(
            EndpointName=endpoint_name, EndpointConfigName=endpoint_config_name)
        print("Update endpoint response = ", update_endpoint_response)
    else:  
        #Create new endpoint
        print('Create new endpoint ', endpoint_name, ' with product_variant:', production_variant)
        model.sagemaker_session.endpoint_from_production_variants(endpoint_name, [production_variant], wait=False)

def get_mapping_index_(origin_subset):
    subset = []
    for character in origin_subset:
        subset.append(char_to_label_index(character))
    return subset

def to_local_tf_record_(user_name, result_folder, origin_subset_name, origin_subset):
    subset = get_mapping_index_(origin_subset)
    print("subset=", subset)
    data_types = ['train', 'validation', 'test']
    data_sets = {}
    if user_name != DEFAULT_USERNAME:
        data_sets = read_data_sets(
            result_folder, dtype=dtypes.uint8, subset = subset, validation_size=5000)
    else:
        emnist_folder = get_emnist_cache_folder()
        data_sets = read_data_sets(
            emnist_folder, prefix="emnist-byclass-", dtype=dtypes.uint8, subset=subset, validation_size=5000)

    local_tf_record_folder = get_local_tf_record_folder(user_name, origin_subset_name) 
    if os.path.exists(local_tf_record_folder): 
        shutil.rmtree(local_tf_record_folder)
    os.makedirs(local_tf_record_folder)

    train_filename = convert_to(data_sets['train'], 'train', local_tf_record_folder)
    validation_filename = convert_to(data_sets['validation'], 'validation', local_tf_record_folder)
    test_filename = convert_to(data_sets['test'], 'test', local_tf_record_folder)
    return train_filename, validation_filename, test_filename

def upload_tfrecord_(user_name, result_folder, origin_subset_name, origin_subset):
    train_filename, validation_filename, test_filename = (
        to_local_tf_record_(user_name, result_folder, origin_subset_name, origin_subset))

    # Get S3 destination
    s3_folder = get_s3_folder_bucket_training_data(user_name, origin_subset_name)
    train_s3 = os.path.join(s3_folder, os.path.split(train_filename)[1])
    validation_s3 = os.path.join(s3_folder, os.path.split(validation_filename)[1])
    test_s3 = os.path.join(s3_folder, os.path.split(test_filename)[1])

    #Upload file to S3
    print("Upload file to S3")
    upload_file(train_s3, train_filename)
    print("Uploaded to : " + train_s3)
    upload_file(validation_s3, validation_filename)
    print("Uploaded to : " + validation_s3)
    upload_file(test_s3, test_filename)
    print("Uploaded to : " + test_s3)

def get_global_step_(checkpoint_path):
    s3 = boto3.resource('s3')
    obj = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).Object('nghia/checkpoint/nghia-0-9-job/checkpoints/checkpoint')
    res = obj.get()['Body'].read().decode('utf-8') 
    first_line = res.split('\n', 1)[0]
    return int(re.search('(?<=ckpt-)\d+', first_line).group(0))

def upload_and_train_(user_name, result_folder, origin_subset_name, origin_subset):

    if ENABLE_STAGE and STAGE==STAGE_UPLOAD:
        upload_tfrecord_(user_name, result_folder, origin_subset_name, origin_subset)
    if not ENABLE_STAGE:
        upload_tfrecord_(user_name, result_folder, origin_subset_name, origin_subset)

    # Setup settings
    print("Start training now for user_name=" + user_name)
    inputs = get_input_training_s3(user_name, origin_subset_name) 
    print("inputs=" + inputs)
    instance_type =  settings.SAGEMAKER_INSTANCE_TYPE
    initial_instance_count = settings.SAGEMAKER_INITIAL_INSTANCE_COUNT
    role = settings.SAGEMAKER_ROLE
    job_name = get_job_name(user_name, origin_subset_name)
    print("Job name =" + job_name)

    # Prepare checkpoint data
    prepare_checkpoint_(origin_subset_name, user_name)
    # Train Data
    user_checkpoint_path = get_s3_checkpoint_path(user_name, origin_subset_name)
    print("S3 Usercheckpoint = ", user_checkpoint_path)
    print("Inputs tfrecord path = ", inputs)

    cur_training_steps = get_global_step_(user_checkpoint_path) + 3000
    mnist_estimator = train_data_(
        inputs, role, job_name, len(origin_subset), 
        user_checkpoint_path,
        instance_type = instance_type, training_steps=cur_training_steps, evaluation_steps=100)
    print("Done with fit for job_name=" + job_name)
    if not mnist_estimator:
        print("Error when executing fit on training data\n\n\n")
        return
    
    if ENABLE_STAGE and STAGE != STAGE_CREATE_ENDPOINT:
        print("Not createing endpoint yet ... Quit!\n\n\n")
        return

    # Create model
    model, model_name = create_model(mnist_estimator, instance_type=instance_type)
    print("Created model name = " + model_name)

    update_endpoint(job_name, model, model_name, user_name, origin_subset_name)

def retrain_newdata(user_name, origin_subset_name, origin_subset):
    print("===========Starting to retrain data:", ','.join(str(x) for x in origin_subset), "===========")
    user_model_folder = get_neural_net_data_folder(user_name)
    trained_filename = os.path.join(user_model_folder, origin_subset_name.replace('-', '_'))
    print("-->Trained filename:", trained_filename)
    model_folder_after_retrain = get_neural_net_data_folder_after_retrain(user_name)
    new_trained_filename = os.path.join(model_folder_after_retrain, origin_subset_name)
    graph = tf.Graph()
    session = tf.Session(graph=graph)
    num_steps = 2 
    mnist_folder = get_mnist_local_folder(user_name)
    mnist = read_data_sets(mnist_folder, prefix="", subset = origin_subset, one_hot = True)
    print(mnist)
    with graph.as_default():
        new_saver = tf.train.import_meta_graph(trained_filename + '.meta') 
        new_saver.restore(session, trained_filename)
        x = graph.get_tensor_by_name("x:0") 
        y_ = graph.get_tensor_by_name("y_:0")
        keep_prob = graph.get_tensor_by_name("keep_prob:0")
        train_step = tf.get_collection("train_step")[0]
        accuracy = tf.get_collection('accuracy')[0]
        train_accuracy = 0.0
        for i in range(num_steps):
            batch = mnist['train'].next_batch(50) 
            if i % 10 == 0:
                train_accuracy = session.run(accuracy, feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
            print('step %d, training accuracy %g' % (i, train_accuracy))    
            session.run(train_step, feed_dict={'x:0': batch[0], 'y_:0': batch[1], keep_prob: 0.5})
        #print('test accuracy %g' % session.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))    
        print("Save to new_trained_filename:" + new_trained_filename)
        new_saver.save(session, new_trained_filename)
        print("<=====Done\n")

@background(schedule=1)
def upload_new_training_record(user_name):
    user = User.objects.get(username=user_name)
    if user and user.email:
        email("Neural network retrain is starting now", user_name, user.email)
    training_image_dir = get_local_train_folder(user_name)
    test_image_dir = training_image_dir
    result_folder = get_mnist_local_folder(user_name)

    local_user_model_folder = get_neural_net_data_folder(user_name)

    # Convert user image to mnist folder
    print("Convert to mnist folder : ")
    print("--> training_image_dir :", training_image_dir)
    print("--> test_image_dir : ", test_image_dir)
    print("--> result_folder : ", result_folder)
    convert_to_mnist(training_image_dir, test_image_dir, result_folder, ACCEPTED_LABEL) 

    remote_model_foldername = get_user_model_remote_folder(user_name)
    print("local_user_model_folder=" + local_user_model_folder)

    model_folder_after_retrain = get_neural_net_data_folder_after_retrain(user_name)
    if os.path.isdir(model_folder_after_retrain): 
        copy_from_trained_neural_net(model_folder_after_retrain, user_name)
    else:    
        copy_master_neural_net_from_default(user_name)
    #
    #for subset in ALL_SUBSETS:
    #    origin_subset_name = subset['name'].replace('-', '_')
    #    remote_model_fullname = os.path.join(remote_model_foldername, origin_subset_name)
    #    local_model_fullname = os.path.join(local_user_model_folder, origin_subset_name)
    #    print("--->Attempt to sync : ")
    #    print("remote_model_fullname=" + remote_model_fullname)
    #    print("local_model_fullname=" + local_model_fullname)
    #    if check_s3_file_exists(remote_model_fullname):
    #        print("=======> Overwrite the local_model_fullname=" + local_model_fullname)
    #        write_file(remote_model_foldername, local_model_fullname)
    #    print("\n")
   
    # Start the training process now.
    for subset in ALL_SUBSETS:
        origin_subset_name = subset['name']
        origin_subset = subset['characters']
        retrain_newdata(user_name, origin_subset_name.replace('-', '_'), origin_subset) 
    user_model_folder = get_neural_net_data_folder(user_name)
    upload_to_s3folder(user_model_folder, remote_model_foldername)
    if user and user.email:
        email("Neural network retrain is done", user_name, user.email)