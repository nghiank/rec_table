import sys, os, shutil
from subprocess import Popen, PIPE
from PIL import Image, ImageFilter
import tensorflow as tf
import numpy as np
import tensorflow as tf
import boto3

num_row = 60
row = [dict() for x in range(num_row+1)]
exp_row = [dict() for x in range(num_row+1)]

attr = ['id', 'num', 'big', 'small', 'roll', 'del', 
        'id', 'num', 'big', 'small', 'roll', 'del']

col_sz = [
    1, 4, 3, 3, 1, 1,
    1, 4, 3, 3, 1, 1
]
num_col = sum(col_sz)

max_length = {
    'id' : 1,
    'num': 4,
    'big': 3,
    'small': 3,
    'roll' : 1,
    'del' : 1
}

# Train data's name
train_data = {
    'day': '2_3_6_7_9',
    'num': '0_9_x_X',
    'big': '0_9',
    'small': '0_9',
    'roll': 'rikRIK', 
    'del': 'dummy',
}

# Letter mapping.
letter_map = {
    'day': '23679',
    'num': '0123456789xX',
    'big': '0123456789',
    'small': '0123456789',
    'roll': 'IKRikr', 
    'del': 'X',
}

# endpoint_name_suffix = {
#     'day': '2-3-6-7-9-ep',
#     'num': '0-9-x-ep',
#     'big': '0-9-ep',
#     'small': '0-9-ep',
#     'roll': 'i-k-r-ep',
# }
# mnist_predictors = {
#    'day': None,
#    'num': None,
#    'big': None,
#    'small': None,
#    'roll': None,
#    'del': None
#} 

#input_filename = "/Users/nghia/rec_table/train/data/test/g.png"
user_name = "nghia"
input_filename = "/Users/nghia/Downloads/a.jpg"
extract_cell_folder = "/Users/nghia/Desktop/tmp"

# Model training data folder for default case
# Each new user will use this to predict the 
# new data. Once user run their own training data set
# new model data will be generated for the user. 
# This model is will be stored on the S3.
trained_data_folder = "../train/checkpoint"

if len(sys.argv) == 4:
    input_filename = sys.argv[1]
    extract_cell_folder = sys.argv[2]
    user_name = sys.argv[3]

fileNamePrefix = 'file'
#client = boto3.client('sagemaker')
#def check_endpoint_exists(endpoint_name):
#    try:
#        response = client.describe_endpoint(
#            EndpointName=endpoint_name
#        ) 
#        #print("describe_endpoint=", response)
#        return response and ('EndpointArn' in response)
#    except:
#        return False
#for key in endpoint_name_suffix:
#    endpoint_name = user_name + "-" + endpoint_name_suffix[key]
#    if check_endpoint_exists(endpoint_name):
#        print("Endpoint name for ", key," -> ", endpoint_name)
#        mnist_predictors[key] = TensorFlowPredictor(endpoint_name)
#    else:
#        default_endpoint_name = "common-" + endpoint_name_suffix[key]
#        mnist_predictors[key] = TensorFlowPredictor(default_endpoint_name)
#        print("Endpoint name for ", key," -> ", default_endpoint_name)

def verify_input():
    global input_filename
    if not os.path.isfile(input_filename):
        print("File %s is missing" % input_filename)
        return False
    return True
    
def print_header(str):
    print("====" + str + "====")

def imageprepare(filename):
    """
    This function returns the pixel values.
    The imput is a png file location.
    """
    img = Image.open(filename).convert('L')
    rect = img.getbbox()
    im = img.crop(rect)
    im.save(filename + '_pressprocessed.png')

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
        newImage.save(filename + '_final.png')
    else:
        #Height is bigger. Heigth becomes 20 pixels. 
        nwidth = int(round((20.0/height*width),0)) #resize width according to ratio height
        if (nwidth == 0): #rare case but minimum is 1 pixel
            nwidth = 1
         # resize and sharpen
        img = im.resize((nwidth,20), Image.ANTIALIAS).filter(ImageFilter.SHARPEN)
        wleft = int(round(((28 - nwidth)/2),0)) #caculate vertical pozition
        newImage.paste(img, (wleft, 4)) #paste resized image on white canvas
        newImage.save(filename + '_final.png')
    tv = list(newImage.getdata()) #get pixel values
    #normalize pixels to 0 and 1. 0 is pure white, 1 is pure black.
    tva = [ (x)*1.0/255.0 for x in tv] 
    return tva

def predict(filenames, trained_filename, letter_map):
    graph = tf.Graph() 
    with graph.as_default():
        new_saver = tf.train.import_meta_graph(trained_filename + '.meta') 
        x = graph.get_tensor_by_name("x:0") 
        keep_prob = graph.get_tensor_by_name("keep_prob:0")
        y_conv = tf.get_collection('y_conv')[0]
        predict = tf.argmax(y_conv, 1)
    res = [None] * len(filenames)
    with tf.Session(graph=graph) as session:
        new_saver.restore(session, trained_filename)
        for idx, filename in enumerate(filenames):
            if os.path.isfile(filename):
                img = imageprepare(filename)
                v_ = session.run(predict, feed_dict = {"x:0": [img], "keep_prob:0": 1.0}) 
                res[idx] = letter_map[v_[0]]
    return res

def sagemaker_predict(filenames, trained_filename, letter_map, mnist_predictor):
    res = [None] * len(filenames)
    for idx, filename in enumerate(filenames):
        if not os.path.isfile(filename):
            continue
        data = imageprepare(filename)
        tensor_proto = tf.make_tensor_proto(values=np.asarray(data), shape=[1, len(data)], dtype=tf.float32)
        predict_response = mnist_predictor.predict(tensor_proto)
        prediction = predict_response['outputs']['classes']['int64Val'][0]
        res[idx] = letter_map[int(prediction)]
    return res
 
def extract_cell():
    print_header("Extracting cell process")
    print("Extracting file: ", input_filename)
    print("The result is in ", extract_cell_folder)
    process = Popen(["../extract/extract_cell", 
            "--inputFileName", input_filename,
            "--outputFolder", extract_cell_folder], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    print("Done extracing cell %d" % exit_code)

def process_id(current_id):
    print("========== Row %d ============" % get_actual_id(current_id))

def getFileName(i):
    return os.path.join(extract_cell_folder, fileNamePrefix + str(i) + '.png')

# Get the fullpath of the model data based on what type of prediction
def getModelFileName(type):
    return os.path.join(trained_data_folder, train_data[type])

def isCellExist(ind):
    return os.path.isfile(getFileName(ind))

def get_day():
    if isCellExist(0):
        return sagemaker_predict([getFileName(0)], getModelFileName('day'), letter_map['day'], mnist_predictors['day'])
    return [0] 

def predictCells(types):
    global attr
    global row
    row[0] = 'aaaaaaaa'
    #Get train data
    print("Predict for the columns:", types)
    train_file_name = getModelFileName(types[0])
    the_map = letter_map[types[0]]
    # mnist_predictor = mnist_predictors[types[0]]
    print("Train file name:", train_file_name)
    print("The letter map:", the_map)

    #Get starting index and max size
    s_ind = [0] * len(types) * 2   # Store starting index
    sz   = [0] * len(types) * 2    # Store the length
    att   = [0] * len(types) * 2   # Store the attribute
    cnt = 0
    cur_ind = num_col  # Starting from second row 
    for i in range(len(attr)):
        if attr[i] in types:
            s_ind[cnt] = cur_ind 
            sz[cnt] = max_length[attr[i]]
            att[cnt] = attr[i]
            cur_ind += sz[cnt]
            cnt = cnt + 1
        else:
            cur_ind += col_sz[i] 

    num_combine_row = num_row // 2

    # Get all cell indices
    inds = []
    for i in range(num_combine_row):
        #Scan each row
        for j in range(len(s_ind)):
            for k in range(sz[j]):
                ind = s_ind[j] + k + i * num_col
                inds.append(ind)

    # Predict each cell indices
    filenames = [None] * len(inds)
    for i in range(len(inds)):
        filenames[i] = getFileName(inds[i])

    if types[0] == 'del': # Special for this column
        res_predict = [''] * len(inds)
        for i in range(len(filenames)):
            if os.path.isfile(filenames[i]):
                res_predict[i] = 'X'
    else:
        # This is using SageMaker but it is too expensive in term of cost
        # res_predict = sagemaker_predict(filenames, train_file_name, the_map, mnist_predictor)
        res_predict = predict(filenames, train_file_name, the_map)
        
    # Debugging purpose
    '''
    for i in range(len(res_predict)):
        if res_predict[i]:
            print("%d: %s" % (inds[i], res_predict[i]))
    '''
    # Build the value indicated in types
    cnt = 0
    for i in range(num_combine_row):
        #Scan each row
        for j in range(len(s_ind)):
            val = ""
            for k in range(sz[j]):
                if res_predict[cnt]:
                    val = val + res_predict[cnt]
                cnt = cnt + 1
            row_ind = i + 1
            if j >= len(types):
                row_ind = row_ind + num_combine_row
            col_name = att[j]
            print("row_ind = %d, attr=%s, val=%s" % (row_ind, col_name, val))
            row[row_ind][col_name] = val.upper() 
            #print row[row_ind]

def verify_result(exp_filename):
    print("Try to verify result...")
    with open(exp_filename, 'r') as myfile:
        datas = myfile.readlines()
    
    for data in datas:
        data = data.replace('\n', '')
        if len(data) == 0: 
            break
        r = data.split(',')
        print(r)
        try:
            rid = int(r[0])
            exp_row[rid]['num'] = r[1]
            exp_row[rid]['big'] = r[2]
            exp_row[rid]['small'] = r[3]
            exp_row[rid]['roll'] = r[4]
            exp_row[rid]['del'] = r[5]
        except:
            print("Exception throw at line : "  + data)
            print("Unexpected error:" + sys.exc_info()[0])
    
    error_cell_count = 0
    error_row_cnt = 0
    for i in range(1, num_row+1):
        s = ""
        found_diff = False
        error_cell_count = error_cell_count + 1
        for j in range(1, len(attr) // 2):
            try:
                e = exp_row[i][attr[j]]
                a = row[i][attr[j]]
                if e.upper() != a.upper():
                    found_diff = True
                    s = s + "-->diff(%s): %s ==> %s\n" % (attr[j], e, a)
            except:
                print("Exception throw at line : "  + str(i))

        if found_diff: 
            error_row_cnt = error_row_cnt + 1
            rr = i * 26
            if i > 30:
                rr = (i-30) * 26 + 13
            print("Diff found in row %i(in cellid %d)" % (i, rr))
            print(s)
    print("Percent row count error: %0.2f" % ((float(error_row_cnt) / float(num_row)) * 100))
    print("Percent cell count error: %0.2f" % ((float(error_row_cnt) / float(num_row * 5)) * 100))

def process_table():
    day = get_day()
    print("Day=" + str(day[0]))
    for i in range(1, num_row + 1):
        row[i]['del'] = ''
    predictCells(['num'])
    predictCells(['big', 'small'])
    predictCells(['roll'])
    predictCells(['del'])
    #print row
    #populateRowDelCheck()

######################## Main entry start from here ################
####################################################################
if not verify_input():
    print("Invalid input!!!")
    sys.exit()
    
extract_cell()
process_table()
print("========Final value=====")
output_filename = os.path.join(os.path.dirname(input_filename), "result.txt")
fout = open(output_filename, 'w')
for i in range(1, num_row + 1):
    fout.write(','.join([
        row[i]['num'],
        row[i]['big'],
        row[i]['small'],
        row[i]['roll'],
        row[i]['del'],
    ]) + '\n')
    print("====Row %d====" % i)
    print("Num: " + row[i]['num'])
    print("B:   " + row[i]['big'])
    print("S:   " + row[i]['small'])
    print("R:   " + row[i]['roll'])
fout.close()
expected_filename = input_filename + ".exp"
if os.path.isfile(expected_filename):
    verify_result(expected_filename)