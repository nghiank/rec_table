import os.path
from django.conf import settings
from catalog.constants import *

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

# Get Mnist data generated from local train folder
def get_mnist_local_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'mnist')

# Get local tensorflow record folder
def get_local_tf_record_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'tfrecord')

def get_mnist_data_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-images-idx3-ubyte')

def get_mnist_label_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-labels-idx1-ubyte')

