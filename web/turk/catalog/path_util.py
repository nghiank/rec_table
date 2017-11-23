import os.path

# Get local output folder of the image file.
def get_local_output_folder(user_name, id):
    return os.path.join('/tmp', user_name, id)

# Get the local output folder of the single character images
# extracted from the prediction process
def get_local_output_cells(user_name, id):
    return os.path.join(get_local_output_folder(user_name, id) , 'cells')

# Get the local train images folder
# where there are multiple label folders which contain the handwritten images of 
# the user.
def get_local_train_folder(user_name, label):
    return os.path.join('/tmp', user_name, 'training-images', str(label))

# Get local neural net pre-trained data folder
def get_neural_net_data(user_name):
    return os.path.join('/tmp', user_name, 'neural')