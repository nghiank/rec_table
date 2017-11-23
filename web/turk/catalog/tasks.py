import os
from shutil import copyfile

from .constants import NROW
from .data_util import read_expected_result
from .models import Cell
from .models import ImageSheet
from .path_util import get_local_output_folder, get_local_output_cells, get_local_train_folder
from background_task import background
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from pathlib import Path
from django.db import IntegrityError

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
    return os.path.join(get_local_train_folder(user_name, label), str(id) + '_' + str(file_order) + FILE_EXT)

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
    for i in range(0, NROW):
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
                        continue
                    train_file_path = get_local_new_train_data(user_name, v, id, file_order)
                    train_folder = get_local_train_folder(user_name, v)
                    if not os.path.exists(train_folder):
                        os.makedirs(train_folder)
                    copyfile(local_file_name, train_file_path)
                    s3_file_name = get_s3_folder_cells(user_name, id, file_order)
                    print("Uploading fileName = " +str(s3_file_name) + " ==> " + str(v) + " from " + str(result[i][j]) + '...index...'+ str(k))
                    file = default_storage.open(s3_file_name, 'w')
                    with open(local_file_name, 'rb') as f:
                        local_file = File(f)
                        for chunk in local_file.chunks():
                            file.write(chunk)
                    file.close()
                    f.close()
                    write_cell_data(s3_file_name, v, item)
    item.state = ImageSheet.PROCESSED
    item.save()

#@background(schedule=60)
def training_local_data(user_name):
    neural_net_folder = get_neural_net_data(user_name)
    if not os.path.exists(train_folder):
        os.makedirs(train_folder) 
    
