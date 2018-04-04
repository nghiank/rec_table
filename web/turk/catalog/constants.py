NROW = 60
FILE_EXT = '.png'
ACCEPTED_LABEL = ['0','1','2','3','4','5','6','7','8', '9', 'R', 'K', 'I', 'r', 'k', 'i']
ATTR = ['num', 'big', 'small', 'roll', 'del']
MAX_LENGTH = [
    4, # 'num': 4,
    3, # 'big': 3,
    3, # 'small': 3,
    1, # 'roll' : 1,
    1, # 'del' : 1
]

START_INDEX = [1] # We do not care about the first column(order column).
for i in range(0, len(MAX_LENGTH)):
    START_INDEX.append(MAX_LENGTH[i] + START_INDEX[i])
NUM_COL = sum(MAX_LENGTH) + 1