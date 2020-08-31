import time
import busio
import board
import adafruit_amg88xx
import numpy as np
from PIL import Image
import cv2
import matplotlib.pyplot as plt
i2c = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c)
 
while True:
    '''for row in amg.pixels:
        # Pad to 1 decimal place
        print(["{0:.1f}".format(temp) for temp in row])
        print("")
    print("\n")'''
    arr=np.array(amg.pixels)
    arrr=((arr-arr.min())/arr.max())*255
    im = Image.fromarray(arrr.astype(np.uint8))
    im.save('th.jpg')
    img=cv2.imread('th.jpg')
    img=cv2.resize(img,(300,300))
    img=cv2.bitwise_not(img)
    cv2.imshow('Image',img)
    if cv2.waitKey(1) &0xFF ==ord('q'):
        break
    print(arr)
    time.sleep(1)