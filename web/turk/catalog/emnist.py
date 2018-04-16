# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Functions for downloading and reading EMNIST data."""

import gzip
import os

import numpy
from six.moves import xrange  # pylint: disable=redefined-builtin
from tensorflow.python.framework import dtypes
from tensorflow.python.framework import random_seed

# CVDF mirror of http://yann.lecun.com/exdb/mnist/
#SOURCE_URL = 'https://storage.googleapis.com/cvdf-datasets/mnist/'


def _read32(bytestream):
  dt = numpy.dtype(numpy.uint32).newbyteorder('>')
  return numpy.frombuffer(bytestream.read(4), dtype=dt)[0]


def extract_images(f):
  """Extract the images into a 4D uint8 numpy array [index, y, x, depth].
  Args:
    f: A file object that can be passed into a gzip reader.
  Returns:
    data: A 4D uint8 numpy array [index, y, x, depth].
  Raises:
    ValueError: If the bytestream does not start with 2051.
  """
  print('Extracting', f.name)
  with gzip.GzipFile(fileobj=f) as bytestream:
    magic = _read32(bytestream)
    if magic != 2051:
      raise ValueError('Invalid magic number %d in MNIST image file: %s' %
                       (magic, f.name))
    num_images = _read32(bytestream)
    rows = _read32(bytestream)
    cols = _read32(bytestream)
    buf = bytestream.read(rows * cols * num_images)
    data = numpy.frombuffer(buf, dtype=numpy.uint8)
    data = data.reshape(num_images, rows, cols, 1)
    #print("Number of bytes = "  + str(len(data.tostring())) + " num_images=" + str(num_images))
    return data


def dense_to_one_hot(labels_dense, num_classes):
  """Convert class labels from scalars to one-hot vectors."""
  num_labels = labels_dense.shape[0]
  index_offset = numpy.arange(num_labels) * num_classes
  labels_one_hot = numpy.zeros((num_labels, num_classes))
  labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
  return labels_one_hot

def extract_labels(f, one_hot=False, num_classes=62):
  """Extract the labels into a 1D uint8 numpy array [index].
  Args:
    f: A file object that can be passed into a gzip reader.
    one_hot: Does one hot encoding for the result.
    num_classes: Number of classes for the one hot encoding.
  Returns:
    labels: a 1D uint8 numpy array.
  Raises:
    ValueError: If the bystream doesn't start with 2049.
  """
  print('Extracting', f.name)
  with gzip.GzipFile(fileobj=f) as bytestream:
    magic = _read32(bytestream)
    if magic != 2049:
      raise ValueError('Invalid magic number %d in MNIST label file: %s' %
                       (magic, f.name))
    num_items = _read32(bytestream)
    buf = bytestream.read(num_items)
    labels = numpy.frombuffer(buf, dtype=numpy.uint8)
    if one_hot:
      return dense_to_one_hot(labels, num_classes)
    return labels

def filter_subset(images, labels, subset, dtype):
    """Filter data only limited to subset"""
    cnt = 0
    for i in xrange(labels.shape[0]):
        if labels[i] in subset:
            cnt = cnt + 1
    nptype = numpy.uint8
    if dtypes is dtypes.float32:
      nptype = numpy.float32 
    new_images = numpy.zeros((cnt, images.shape[1], images.shape[2], images.shape[3]), dtype=nptype)
    new_labels = numpy.zeros(cnt, dtype=nptype)
    cnt = 0
    for i in xrange(labels.shape[0]):
        if labels[i] in subset:
            new_labels[cnt] = labels[i]
            # Image is flipped
            new_images[cnt] = numpy.rot90(numpy.flip(images[i], 0),3)
            cnt = cnt + 1 
    return new_images, new_labels

def remapping(label, subset):
    """Remapping label to the item index found in subset"""
    return numpy.searchsorted(subset, label)
    
def balance_data(images, labels, num_labels):
  """
  Balance data by making each label has same length with the smallest size.
  """
  print("Balance the data")
  cnt = [0] * num_labels
  n = labels.shape[0]
  for i in range(n):
    cnt[labels[i]] = cnt[labels[i]] + 1
  mmin = min(cnt)
  print("cnt=", cnt, " mmin=", mmin)
  total = mmin * num_labels
  bal = [mmin] * num_labels
  new_images = numpy.zeros((total, images.shape[1], images.shape[2], images.shape[3]), dtype=numpy.uint8)
  new_labels = numpy.zeros(total, dtype=numpy.uint8)
  j = 0
  for i in range(n):
    label = labels[i]
    if bal[label] > 0:
      bal[label] = bal[label] - 1
      new_images[j] = images[i]
      new_labels[j] = label
      j = j + 1
  print("new_images.shape", new_images.shape)
  print("new_labels.shape", new_labels.shape)
  # Shuffle the data
  perm = numpy.arange(j)
  numpy.random.shuffle(perm)
  res_images = new_images[perm]
  res_labels = new_labels[perm]
  return res_images, res_labels

class DataSet(object):
  def __init__(self,
               images,
               labels):
    """
    Construct a DataSet.
    """
    assert images.shape[0] == labels.shape[0], (
        'images.shape: %s labels.shape: %s' % (images.shape, labels.shape))
    self._num_examples = images.shape[0]

    # Shuffle the data
    perm = numpy.arange(self._num_examples)
    numpy.random.shuffle(perm)
    self._images = images[perm]
    self._labels = labels[perm]

  @property
  def images(self):
    return self._images

  @property
  def labels(self):
    return self._labels

  @property
  def num_examples(self):
    return self._num_examples


# Merge two DataSet
def merge_data_set(data_set1, data_set2):
  assert data_set1.images.shape[1:] == data_set2.images.shape[1:], (
    'data_set1.shape: %s , data_set2: %s' % (data_set1.images.shape[1:], data_set2.images.shape[1:]))
  assert data_set1.labels.shape[1:] == data_set2.labels.shape[1:], (
    'data_set1.shape: %s , data_set2: %s' % (data_set1.labels.shape, data_set2.labels.shape))
  merged_images = numpy.concatenate((data_set1.images, data_set2.images), axis=0)
  merged_labels = numpy.concatenate((data_set1.labels, data_set2.labels), axis=0)
  return DataSet(merged_images, merged_labels)


def read_data_sets(train_dir,
                   prefix="",
                   subset = [0,1,2,3,4,5,6,7,8,9],
                   one_hot=False,
                   dtype=dtypes.float32,
                   reshape=False,
                   validation_size=500,
                   seed=None):
  TRAIN_IMAGES = prefix + 'train-images-idx3-ubyte.gz'
  TRAIN_LABELS = prefix + 'train-labels-idx1-ubyte.gz'
  TEST_IMAGES = prefix + 'test-images-idx3-ubyte.gz'
  TEST_LABELS = prefix + 'test-labels-idx1-ubyte.gz'

  local_file = os.path.join(train_dir, TRAIN_IMAGES)
  with open(local_file, 'rb') as f:
    train_images = extract_images(f)

  local_file = os.path.join(train_dir, TRAIN_LABELS)
  with open(local_file, 'rb') as f:
    train_labels = extract_labels(f, one_hot=one_hot)

  local_file = os.path.join(train_dir, TEST_IMAGES)
  with open(local_file, 'rb') as f:
    test_images = extract_images(f)

  local_file = os.path.join(train_dir, TEST_LABELS)
  with open(local_file, 'rb') as f:
    test_labels = extract_labels(f, one_hot=one_hot)

  print("Number of bytes found = "  + str(len(train_images.tostring())) + " num_images=" + str(train_images.shape[0]))

  train_images, train_labels = filter_subset(train_images, train_labels, subset, dtype)
  test_images, test_labels = filter_subset(test_images, test_labels, subset, dtype)
  print("Number of bytes found  after filter= "  + str(len(train_images.tostring())) + " num_images=" + str(train_images.shape[0]))

  train_labels = remapping(train_labels, subset)
  test_labels = remapping(test_labels, subset)


  validation_size = min(validation_size, int(len(train_images)/9))
  validation_images = train_images[:validation_size]
  validation_labels = train_labels[:validation_size]
  train_images = train_images[validation_size:]
  train_labels = train_labels[validation_size:]

  train_images, train_labels = balance_data(train_images, train_labels, len(subset))
  validation_images, validation_labels = balance_data(validation_images, validation_labels, len(subset))
  test_images, test_labels = balance_data(test_images, test_labels, len(subset))

  train = DataSet(train_images, train_labels)
  validation = DataSet(validation_images, validation_labels)
  test = DataSet(test_images, test_labels)
  return {'train':train, 'validation':validation, 'test':test}


def load_mnist(train_dir='MNIST-data'):
  return read_data_sets(train_dir)