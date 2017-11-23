import os.path

# Get local output folder of the image file.
def get_local_output_folder(user_name, id):
    return os.path.join('/tmp', user_name, id)

# Get the local output folder of the single character images
# extracted from the prediction process
def get_local_output_cells(user_name, id):
    return os.path.join(get_local_output_folder(user_name, id) , 'cells')
