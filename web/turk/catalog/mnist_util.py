import os
import shutil
from PIL import Image
from array import *
from random import shuffle
from .path_util import get_mnist_data_file_name, get_mnist_label_file_name

def convert_to_mnist(train_data_folder, test_data_folder, result_folder, accepted_label):
    # Load from and save to
    Names = [[train_data_folder,'train'], [test_data_folder,'test']]
    if os.path.exists(result_folder): 
        shutil.rmtree(result_folder)
    os.makedirs(result_folder)
    for name in Names:
        data_image = array('B')
        data_label = array('B')
        FileList = []
        for dirname in os.listdir(name[0]): 
            if dirname not in accepted_label:
                continue
            path = os.path.join(name[0],dirname)
            for filename in os.listdir(path):
                if filename.endswith(".png"):
                    FileList.append(os.path.join(name[0],dirname,filename))
        shuffle(FileList) # Usefull for further segmenting the validation set
        print("FileList:" + str(FileList))
        for filename in FileList:
            label = ord(os.path.split(os.path.dirname(filename))[1]) - ord('0')
            print("Current label:" + str(label), ' filename='+filename)
            Im = Image.open(filename)
            pixel = Im.load()
            width, height = Im.size
            print("Width=" + str(width) + " ,height=" + str(height))
            for x in range(0,width):
                for y in range(0,height):
                    #print("y=" + str(y) + " ,x="+str(x))
                    data_image.append(pixel[x,y])
            data_label.append(label) # labels start (one unsigned byte each)
        hexval = "{0:#0{1}x}".format(len(FileList),6) # number of files in HEX

        # header for label array
        header = array('B')
        header.extend([0,0,8,1,0,0])
        header.append(int('0x'+hexval[2:][:2],16))
        header.append(int('0x'+hexval[2:][2:],16))
        data_label = header + data_label

        # additional header for images array
        
        if max([width,height]) <= 256:
            header.extend([0,0,0,width,0,0,0,height])
        else:
            raise ValueError('Image exceeds maximum size: 256x256 pixels');

        header[3] = 3 # Changing MSB for image data (0x00000803)
        
        data_image = header + data_image

        #output_file = open(name[1]+'-images-idx3-ubyte', 'wb')
        print("SAve output")
        output_file = open(get_mnist_data_file_name(result_folder, name[1]), 'wb')
        data_image.tofile(output_file)
        output_file.close()

        output_file = open(get_mnist_label_file_name(result_folder, name[1]), 'wb')
        data_label.tofile(output_file)
        output_file.close()
    # gzip resulting files
    for name in Names:
        os.system('gzip '+ get_mnist_data_file_name(result_folder, name[1]))
        os.system('gzip '+ get_mnist_label_file_name(result_folder, name[1]))