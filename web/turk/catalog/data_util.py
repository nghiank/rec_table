import os.path
import collections
from PIL import Image, ImageFilter
from catalog.constants import *
from catalog.models import ExpectedResult
from catalog.path_util import *
from django.core.files import File
from django.core.files.storage import default_storage

def read_predicted_result(local_output_folder):
    # The result is written in result.txt
    output_result = os.path.join(local_output_folder, 'result.txt')
    with open(output_result) as f:
        content = f.readlines()
    content = [x.strip() for x in content] 
    result = [x.split(",") for x in content]
    return result

def read_expected_result(expected_results):
    er = []
    for i in range(0,60):
        er.append({})
    for expected_result in expected_results:
        r = int(expected_result.order) - 1
        er[int(expected_result.order) - 1] = [
            expected_result.num,
            expected_result.big,
            expected_result.small,
            expected_result.roll,
            expected_result.is_delete,
        ]
    return er

def padding_space(v, max_len):
    while len(v) < max_len:
        v = ' ' + v
    return v

def extract_character(value, index):
    if len(value) <= index or value[index] == ' ':
        return None
    return value[index]

def get_file_name(row, col, sub_col, folder):
    if row < (NROW // 2):
        result = (2*NUM_COL) * (row + 1) + START_INDEX[col] + sub_col
    else:
        result = (2*NUM_COL) * (row - 29) + NUM_COL + START_INDEX[col] + sub_col
    return (os.path.join(folder, 'file' + str(result) + FILE_EXT), result)

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

def get_all_local_data_for_user(user_name):
    """
    Get all label image data for a user which categorize based on the label folder
    and each label folder contains all images for that label image
    """
    local_image_folder = get_local_train_folder(user_name)
    label_img = {}
    for label in os.listdir(local_image_folder): 
        if label not in ACCEPTED_LABEL:
            continue
        dirname = os.path.join(local_image_folder, label)
        print("Label name = " + dirname)
        for file in os.listdir(dirname):
            _, extension = os.path.splitext(file)
            if extension not in [".png", ".jpg", "jpeg"]:
                continue
            if label not in label_img:
                label_img[label] = []
            full_path = os.path.join(get_relative_local_train_folder(user_name), label, file)
            full_path = os.path.join('/media', full_path)
            label_img[label].append(full_path)
    label_img_sorted = collections.OrderedDict(sorted(label_img.items()))
    return label_img_sorted

"""Converts MNIST data to TFRecords file format with Example protos."""
import os
import tensorflow as tf

def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def convert_to(data_set, name, directory):
    """Converts a dataset to tfrecords."""
    images = data_set.images
    labels = data_set.labels
    num_examples = data_set.num_examples

    print("Images shape:" + str(images.shape))
    if images.shape[0] != num_examples:
        raise ValueError('Images size %d does not match label size %d.' %
                         (images.shape[0], num_examples))
    rows = images.shape[1]
    cols = images.shape[2]
    depth = images.shape[3]
    print("Rows = " + str(rows))
    print("Cols = " + str(cols))
    print("Depth = " + str(depth))
    filename = os.path.join(directory, name + '.tfrecords')
    print('Writing', filename)
    writer = tf.python_io.TFRecordWriter(filename)
    for index in range(num_examples):
        image_raw = images[index].tostring()
        example = tf.train.Example(features=tf.train.Features(feature={
            'height': _int64_feature(rows),
            'width': _int64_feature(cols),
            'depth': _int64_feature(depth),
            'label': _int64_feature(int(labels[index])),
            'image_raw': _bytes_feature(image_raw)}))
        writer.write(example.SerializeToString())
    writer.close()
    return filename

def upload_file(s3_file_name, local_file_name):
    file = default_storage.open(s3_file_name, 'w')
    with open(local_file_name, 'rb') as f:
        local_file = File(f)
        for chunk in local_file.chunks():
            file.write(chunk)
    file.close()
    f.close()