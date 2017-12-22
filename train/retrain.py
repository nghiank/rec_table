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
from tensorflow.examples.tutorials.mnist import input_data

subset = [0,1,2,3,4,5,6,7,8,9,33,59]  
mnist = emnist.read_data_sets('/Users/nghia/tmp/nghia/mnist', prefix="", validation_size=10, subset = subset) 
#mnist = emnist.read_data_sets('data/emnist', subset = subset)
print("Number of train images=" + str(mnist.train.images.shape))
start = time.clock()
# Retrain from last checkpoint 
trained_filename = '/Users/nghia/rec_table/train/checkpoint/0_9_x'
new_trained_filename = '/Users/nghia/rec_table/train/checkpoint/0_9_x'
num_steps = 300


# We can now access the default graph where all our metadata has been loaded
graph = tf.Graph()
session = tf.Session(graph=graph)
print("Starting retrain...")
with graph.as_default():
    new_saver = tf.train.import_meta_graph(trained_filename + '.meta') 
    new_saver.restore(session, trained_filename)
    x = graph.get_tensor_by_name("x:0") 
    y_ = graph.get_tensor_by_name("y_:0")
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    train_step = tf.get_collection("train_step")[0]
    accuracy = tf.get_collection('accuracy')[0]
    for i in range(num_steps):
        batch = mnist.train.next_batch(50) 
        if i % 100 == 0:
            train_accuracy = session.run(accuracy, feed_dict={x: batch[0], y_: batch[1], keep_prob: 1.0})
            print('step %d, training accuracy %g' % (i, train_accuracy))
            
        session.run(train_step, feed_dict={'x:0': batch[0], 'y_:0': batch[1], keep_prob: 0.5})
    print('test accuracy %g' % session.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 1.0}))    
    new_saver.save(session, new_trained_filename)