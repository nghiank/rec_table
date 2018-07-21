import os.path
import collections
from PIL import Image, ImageFilter
from catalog.constants import *
from catalog.models import ExpectedResult
from catalog.path_util import *
from django.core.files import File
from django.core.files.storage import default_storage
import sys
import boto3
import botocore

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
    print("Saving image " + newfilename)
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

    if images.shape[0] != num_examples:
        raise ValueError('Images size %d does not match label size %d.' %
                         (images.shape[0], num_examples))
    rows = images.shape[1]
    cols = images.shape[2]
    depth = images.shape[3]
    filename = os.path.join(directory, name + '.tfrecords')
    print('=======Writing', filename)
    print("Images shape:" + str(images.shape) + " num_examples:" + str(num_examples))
    writer = tf.python_io.TFRecordWriter(filename)
    #  num_examples = 100
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
    print("Write to ", filename, " done")
    return filename

def upload_to_s3folder(local_folder, s3_folder):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
    for f in os.listdir(local_folder):
        filename = os.path.join(local_folder, f)
        if os.path.isfile(filename):
            s3_filename = os.path.join(s3_folder, f)
            data = open(filename, 'rb')
            print("Uploading..." + filename + " to s3 folder:" + s3_filename)
            bucket.put_object(Key=s3_filename, Body=data)
            print("<--Done:" + filename)

def upload_file(s3_file_name, local_file_name):
    print("Upload data to S3:", local_file_name, "-->", s3_file_name)
    file = default_storage.open(s3_file_name, 'w')
    with open(local_file_name, 'rb') as f:
        cnt = 0
        local_file = File(f)
        sz = local_file.size
        print("File size:", sz)
        for chunk in local_file.chunks():
            print("Writing chunks:", cnt, "/", sz, " progress=", (float(cnt) / float(sz) * 100.0))
            file.write(chunk)
            cnt = cnt + 64 * 1024 
        print("Writing chunks:", sz, "/", sz)
    file.close()
    f.close()

def write_file(s3_file_name, local_file_name):
    file = default_storage.open(s3_file_name, 'r')
    with open(local_file_name, 'wb') as f:
        local_file = File(f)
        for chunk in file.chunks():
            local_file.write(chunk)
    file.close()
    f.close()

# Convert character to label mapping
def char_to_label_index(c):
  """
  '0' -> '9' : 0 -> 9
  'A' -> 'Z' : 10 -> 35
  'a' -> 'z' : 36 -> 61
  """
  if c>='0' and c<='9':
    return ord(c) - ord('0')
  if c>='A' and c<='Z':
    return ord(c) - ord('A') + 10
  return ord(c) - ord('a') + 36

# Check if a folder exists in s3.
def check_s3_folder_exist(folder_path, bucket_name=settings.AWS_STORAGE_BUCKET_NAME):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    size = 0
    for obj in bucket.objects.filter(Prefix=folder_path): 
        path, filename = os.path.split(obj.key)
        if not filename:
            continue
        size = size + 1
    print("size=" + str(size))
    return size > 0

def  check_s3_file_exists(s3_file_path):
    s3 = boto3.resource('s3')
    try:
        s3.Object(settings.AWS_STORAGE_BUCKET_NAME, s3_file_path).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            return False
    return True

def copy_s3_folder(src, dst, bucket_name = settings.AWS_STORAGE_BUCKET_NAME):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=src):
        old_source = { 
            'Bucket': bucket_name,
            'Key': obj.key}
        # replace the prefix
        new_key = obj.key.replace(src, dst)
        new_obj = bucket.Object(new_key)
        new_obj.copy(old_source)

def download_s3_folder(remote_src, local_dst, bucket_name = settings.AWS_STORAGE_BUCKET_NAME):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=remote_src): 
        path, filename = os.path.split(obj.key)
        if not filename:
            continue
        write_file(obj.key, os.path.join(local_dst, filename))
        