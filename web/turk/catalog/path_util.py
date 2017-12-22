import os.path
from django.conf import settings

# Get local output folder of the image file.
def get_local_output_folder(user_name, id):
    return os.path.join(settings.TMP_DIR, user_name, id)

# Get the local output folder of the single character images
# extracted from the prediction process
def get_local_output_cells(user_name, id):
    return os.path.join(get_local_output_folder(user_name, id) , 'cells')

# Get the local train folder that contains all label
def get_local_train_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'training-images')

# Get the local train images folder for a label
# where there are multiple label folders which contain the handwritten images of 
# the user.
def get_local_train_folder_for_label(user_name, label):
    return os.path.join(settings.TMP_DIR, user_name, 'training-images', str(label))

# Get the local test images folder
# where there are multiple label folders which contain the handwritten images of 
# the user.
def get_local_test_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'test-images')

# Get local neural net pre-trained data folder
def get_neural_net_data_folder(user_name):
    return os.path.join(settings.TMP_DIR, user_name, 'neural')

def get_mnist_data_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-images-idx3-ubyte')

def get_mnist_label_file_name(result_folder, name):
    return os.path.join(result_folder, name + '-labels-idx1-ubyte')