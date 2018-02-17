import numpy as np
import datetime
import time

local = time.strftime('%b %d %H:%M:%S')

# print(local)

lst = [['abc', '123'],['def', '345']]

super = np.array(lst)


for i in super:
	print(i[0], i[1], local)

# print(np.array)