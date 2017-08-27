import tensorflow as tf
import numpy as np
import sys
from PIL import Image, ImageFilter
import numpy

trained_filename = sys.argv[1]
predict_filename = sys.argv[2]
predict_column = sys.argv[3]

def imageprepare(filename):
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
    tv = list(newImage.getdata()) #get pixel values
    #normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [ (x)*1.0/255.0 for x in tv] 
    return tva
    #print(tva)

graph = tf.Graph() 
with graph.as_default():
    filename = predict_filename
    img = imageprepare(filename)
'''
image_size = 28
predict_image = np.array(img)
predict_image = predict_image.reshape([image_size, image_size])
plt.imshow(predict_image, aspect="auto") 
'''

graph = tf.Graph() 

letter_map = ['I', 'K', 'R', 'i', 'k', 'r']
#letter_map = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
#print("Label:", mnist.train.labels[tt])
#print("Label:", letter_map[np.argmax(mnist.train.labels[tt])])
#plt.imshow(show_image, aspect="auto") 
#print(show_image)


with graph.as_default():
    new_saver = tf.train.import_meta_graph(trained_filename + '.meta') 
    x = graph.get_tensor_by_name("x:0") 
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    y_conv = tf.get_collection('y_conv')[0]
    predict = tf.argmax(y_conv, 1)
with tf.Session(graph=graph) as session:
    new_saver.restore(session, trained_filename)
    v_ = session.run(predict, feed_dict = {"x:0": [img], "keep_prob:0": 1.0}) 
    #print(v_)
print(letter_map[v_[0]])
    
    


