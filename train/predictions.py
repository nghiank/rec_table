image_size = 28 

graph = tf.Graph() 
with graph.as_default():
    
    # Make a queue of file names including all the JPEG images files in the relative
    # image directory.
    filenames = tf.train.match_filenames_once("/Users/nghiaround/Desktop/out/file6.png")
    filename_queue = tf.train.string_input_producer(filenames)

    # Read an entire image file which is required since they're JPEGs, if the images
    # are too large they could be split in advance to smaller files or use the Fixed
    # reader to split up the file.
    image_reader = tf.WholeFileReader()

    # Read a whole file from the queue, the first returned value in the tuple is the
    # filename which we are ignoring.
    _, image_file = image_reader.read(filename_queue)

    # Decode the image as a PNG file, this will turn it into a Tensor which we can
    # then use in training.
    image = tf.image.decode_png(image_file)

    #print(image.shape)
    grayscale_img = tf.image.rgb_to_grayscale(image)
    #print('shape=', grayscale_img.shape(0), grayscale_img.shape(1))


    #final_img = tf.reshape(resized_img, [image_size, image_size]).astype(np.float32)

    #new_img = grayscale_img.reshape([image_size, image_size])

# Start a new session to show example output.
with tf.Session(graph=graph) as sess:
    # Required to get the filename matching to run.
    tf.initialize_all_variables().run()

    # Coordinate the loading of image files.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    # get image
    names = sess.run(filenames)
    print("File names=", names)
    tmp_img = sess.run(grayscale_img)
    tmp_img = (255.0 - tmp_img) 
    tmp_img = tmp_img / 255.0
    tmp_img[tmp_img > 0.5] = 1.0
    tmp_img[tmp_img < 0.5] = 0.0
    #tmp_img = tmp_img.reshape([74,56])
    #print('tmp.img', tmp_img.shape)
    #plt.imshow(tmp_img, aspect="auto") 
    
    mmax = max(tmp_img.shape)
    resized_img = tf.image.resize_image_with_crop_or_pad(tmp_img, 2 * mmax, 2 * mmax)
    resized_img = tf.image.resize_images(resized_img, 28, 28, tf.image.ResizeMethod.BILINEAR)
    
    # Get an image tensor and print its value.
    image_tensor = sess.run(resized_img)
    
    image_tensor = image_tensor.reshape([28, 28]).astype(np.float32)
    #image_tensor = 255 - image_tensor
    
    
    #print(image_tensor)
    plt.imshow(image_tensor, aspect="auto") 
    
    #print(image_tensor.shape)
    
    
    #Image.fromarray(np.asarray(image_tensor)).show()
    

    # Finish off the filename queue coordinator.
    coord.request_stop()
    coord.join(threads)

    

#print('shape:', mnist.test.images.shape) 
one_image = mnist.test.images[100] 
show_image = one_image.reshape([image_size, image_size])
#plt.imshow(show_image, aspect="auto")
#display(Image(filename='/Users/nghiaround/Documents/tess/TestTesseract/TestTesseract/file0.png'))
#display(Image(data=one_image))
#one_image = np.expand_dims(one_image, axis=1)
#print('shape of one_image:', one_image.shape)
#img_input = one_image.reshape([1, image_size * image_size]).astype(np.float32)
#print('one image dtype', one_image.dtype) 
#print('image input shape:', img_input.shape) 
#batch = mnist.train.next_batch(1)[0]
#print('batch shape :' , batch.shape) 
#print('img_input dtype', img_input.dtype) 
graph = tf.Graph() 

img_input = image_tensor.reshape([1, image_size * image_size]).astype(np.float32)
#img_input = one_image.reshape([1, image_size * image_size]).astype(np.float32)
#print(show_image)


with graph.as_default():
    #resized_images=tf.image.resize_images(images, 28, 28, tf.image.ResizeMethod.BILINEAR)

    new_saver = tf.train.import_meta_graph('/Users/nghiaround/Documents/tess/my_mnist_model.meta') 
    x = graph.get_tensor_by_name("x:0") 
    keep_prob = graph.get_tensor_by_name("keep_prob:0")
    #Now, access the op that you want to run. y_conv = graph.get_operation_by_name('y_conv') print(sess.run('b_fc2:0'))
    #print(sess.run('W_conv1:0')) y_conv = tf.get_collection('y_conv')[0] 
    #x_image = tf.get_collection('x_image')[0] 
    #x_image1 = tf.reshape(x, [-1, 28, 28, 1], name='x_image1')
    #h_conv1 = tf.get_collection('h_conv1')[0]
    #h_pool1 = tf.get_collection('h_pool1')[0]
    #h_fc1 = tf.get_collection('h_fc1')[0]
    #y_conv = tf.get_collection('y_conv')[0]
    #h_fc1_drop = tf.get_collection('h_fc1_drop')[0]
    y_conv = tf.get_collection('y_conv')[0]
    predict = tf.argmax(y_conv, 1)
with tf.Session(graph=graph) as session:
    new_saver.restore(session, '/Users/nghiaround/Documents/tess/my_mnist_model')
    v_ = session.run(predict, feed_dict = {"x:0": img_input, "keep_prob:0": 1.0}) 
    print(v_)
    