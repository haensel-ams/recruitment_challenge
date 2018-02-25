from random import random
from time import sleep
from sys import exit

print("Running step2... ",end="",flush=True)

sleep(1800 + 3*3600*random())

if (random() > 0.999):
    print("FAILED!")
    exit(1)

print("DONE!")

