NROW = 60
DEFAULT_USERNAME = "common"
FILE_EXT = '.png'
ACCEPTED_LABEL = ['0','1','2','3','4','5','6','7','8', '9', 'R', 'K', 'I', 'r', 'k', 'i', 'x', 'X']
ATTR = ['num', 'big', 'small', 'roll', 'del']
MAX_LENGTH = [
    4, # 'num': 4,
    3, # 'big': 3,
    3, # 'small': 3,
    1, # 'roll' : 1,
    1, # 'del' : 1
]

ALL_SUBSETS = [
    {
        'name': '0-9',
        'characters':[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],   
    },
    {
        'name': '0-9-x-X',
        #'characters': [0,1,2,3,4,5,6,7,8,9,X,x],   
        'characters': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 33, 59],   
    },
    {
        'name': '2-3-6-7-9',
        'characters': [2, 3, 6, 7, 9],  

    },
    {
        'name': 'rikRIK',
        #'characters': ['I', 'K', 'R', 'i','k','r'],
        'characters': [18, 20, 27, 44, 46, 53]  # the number follow the index from emnist dataset
    },
]

START_INDEX = [1] # We do not care about the first column(order column).
for i in range(0, len(MAX_LENGTH)):
    START_INDEX.append(MAX_LENGTH[i] + START_INDEX[i])
NUM_COL = sum(MAX_LENGTH) + 1

