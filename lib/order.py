import hmac
import hashlib
import base64

your_bytes_string='This is a string'

dig = hmac.new(b'1234567890', msg=your_bytes_string, digestmod=hashlib.sha256).digest()
base64.b64encode(dig).decode()      # py3k-mode
'Nace+U3Az4OhN7tISqgs1vdLBHBEijWcBeCqL5xN9xg='













# import time

# import requests
# import pprint
# import pickle
# import numpy as np
# import csv


# class CreateOrder:
# 	def __init__(self):

