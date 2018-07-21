import os.path
from django.conf import settings
from catalog.constants import *


# Get common emnist data
def get_emnist_cache_folder():
    return os.path.join(settings.TMP_DIR, 'emnist')

# Get local output folder of the image file.
def get_local_output_folder(user_name, id):
    return os.path.join(settings.TMP_DIR, user_name, id)

# Get the local output folder of the single character images
# extracted from the prediction process
def get_local_output_cells(user_name, id):
    return os.path.join(get_local_output_folder(user_name, id) , 'cells')

# Get the relative local train folder
def get_relative_local_train_folder(user_name):
    return os.path.join(user_name, 'training-images')

# Get the local train folder that contains all label
def get_local_train_folder(user_name):
    return os.path.join(settings.TMP_DIR, get_relative_local_train_folder(user_name))

# Get the local train images folder for a label
# where there are multiple label folders which contain the handwritten images of 
# the user.
def get_local_train_folder_for_label(user_name, label):
    return os.path.join(settings.TMP_DIR, user_name, 'training-images', str(label))

def get_local_new_train_data(user_name, label, id, file_order):
    return os.path.join(get_local_train_folder_for_label(user_name, label), str(id) + '_' + str(file_order) + FILE_EXT)

# Get the local test images folder
# where there are multiple label folders which contain the handwritten images of 
# the user.
def get_local_test_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'test-images')

# Get local neural net pre-trained data folder
def get_neural_net_data_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'neural')

# Get local neural net data after retraining.
def get_neural_net_data_folder_after_retrain(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'neural_after_retrain')

# Get Mnist data generated from local train folder
def get_mnist_local_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'mnist')

# Get local tensorflow record folder for each subset
def get_local_tf_record_folder(user_name, subset_name):
    return os.path.join(settings.TMP_DIR, user_name, 'tfrecord', subset_name)

def get_mnist_data_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-images-idx3-ubyte')

def get_mnist_label_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-labels-idx1-ubyte')

def get_s3_folder_bucket_training_data(user_name, subset_name):
    return os.path.join(settings.TRAINING_DATA_BUCKET, user_name, 'tfrecord', subset_name)

def get_user_model_remote_folder(user_name):
   """
      Return as : "training-data-dev/nghia"
   """
   return os.path.join(settings.TRAINING_DATA_BUCKET, user_name)

def get_input_training_s3(user_name, origin_subset_name):
   """
    Return as : "s3://imagesheet1/training-data-dev/nghia/tfrecord/0-9"
   """
   path = "s3://" + settings.AWS_STORAGE_BUCKET_NAME
   path += "/" + get_s3_folder_bucket_training_data(user_name, origin_subset_name)
   return path

def get_user_checkpoint(user_name, origin_subset_name):
    return os.path.join(user_name, 'checkpoint', user_name + '-' + origin_subset_name.replace('_','-') + '-job') 

def get_s3_checkpoint_path(user_name, origin_subset_name):
    path = "s3://" + settings.AWS_STORAGE_BUCKET_NAME
    path += "/" + get_user_checkpoint(user_name, origin_subset_name) + "/checkpoints"
    return path