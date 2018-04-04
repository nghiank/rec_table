import os.path
from .models import ExpectedResult
from catalog.constants import *
from PIL import Image, ImageFilter

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