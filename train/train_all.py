'''
Sample run:

Train only I,K,R,i,k,r
python train_all.py ~/rec_table/train/checkpoint/rikRIK 18,20,27,44,46,53 I,K,R,i,k,r

Train only 0,1,2,3,4,5,6,7,8,9,x,X
python train_all.py ~/rec_table/train/checkpoint/0_9_x 0,1,2,3,4,5,6,7,8,9,33,59 0,1,2,3,4,5,6,7,8,9,X,x ~/rec_table/train/checkpoint/zeroToNineXx

'''

import tensorflow as tf
import time
import numpy as np
import emnist
import sys
from PIL import Image

def weight_variable(shape, name):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial, name=name)

def bias_variable(shape, name):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial, name=name)

def conv2d(x, W, name=None):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME', name=name)

def max_pool_2x2(x, name):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1],
                        strides=[1, 2, 2, 1], padding='SAME', name=name)

start = time.clock()

trained_filename = sys.argv[1]
subset = sys.argv[2].split(',')
for i in range(len(subset)):
    subset[i] = int(subset[i])
mapping = sys.argv[3].split(',')
print("subset=", subset)
print("mapping=", mapping)
print("trained file name=", trained_filename)

mnist = emnist.read_data_sets('data/emnist', subset = subset)

image_size = 28
num_label = len(subset)
num_steps = 20000 

graph = tf.Graph()
print("Start training..., number of steps = ", num_steps)
print("mnist.train.next_batch(50):" ,mnist.train.next_batch(50)[0].shape)
with graph.as_default():  
    x = tf.placeholder(tf.float32, shape=[None, 784], name='x')
    y_ = tf.placeholder(tf.float32, shape=[None, num_label], name='y_')
    global_step = tf.Variable(0, name='global_step', trainable=False)
       
    W_conv1 = weight_variable([5, 5, 1, 32], 'W_conv1')
    b_conv1 = bias_variable([32], 'b_conv1')
    x_image = tf.reshape(x, [-1, 28, 28, 1], name='x_image')
                        

    h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1, name='h_conv1')
    h_pool1 = max_pool_2x2(h_conv1, 'h_pool1')
    W_conv2 = weight_variable([5, 5, 32, 64], 'W_conv2')
    b_conv2 = bias_variable([64], 'b_conv2')
    h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
    h_pool2 = max_pool_2x2(h_conv2, 'h_pool2')
    W_fc1 = weight_variable([7 * 7 * 64, 1024], 'W_fc1')
    b_fc1 = bias_variable([1024], 'b_fc1')
    h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
    h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
    keep_prob = tf.placeholder(tf.float32, name='keep_prob')
    h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)
    W_fc2 = weight_variable([1024, num_label], 'W_fc2')
    b_fc2 = bias_variable([num_label], 'b_fc2')

    y_conv = tf.identity(tf.matmul(h_fc1_drop, W_fc2) + b_fc2,name='y_conv')
    tf.add_to_collection('y_conv', y_conv)
    
    
    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_conv))
    train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    tf.add_to_collection('accuracy', accuracy)
    tf.add_to_collection("train_step", train_step)

print('mnist.test_images.shape', mnist.test.images.shape)
print('mnist.test_labels.shape', mnist.test.labels.shape)

print('Test label shape = ', mnist.test.labels.shape)
with tf.Session(graph=graph) as session:
    session.run(tf.global_variables_initializer())
    saver = tf.train.Saver()
    for i in range(num_steps):
        batch = mnist.train.next_batch(num_label)
        if i % 100 == 0:
            train_accuracy = accuracy.eval(feed_dict={
                x: batch[0], y_: batch[1], keep_prob: 1.0})
            print('step %d, training accuracy %g' % (i, train_accuracy))
            
        train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.5})
    print('Calculate the accuracy again test...')
    #print('-->Test accuracy %g' % accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))
    saver.save(session, trained_filename)



