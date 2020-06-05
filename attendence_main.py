'''import tkinter as tk
import time

# --- functions ---

def check():
    # update text in existing labels
    label['text'] = time.strftime('%H:%M:%S')

    # run again after 1000ms (1s)
    root.after(1000, check) 

# --- main ---

root = tk.Tk()

label = tk.Label(root)
label.pack()

check() # run first time

root.mainloop()

'''

from guizero import App , Picture, Text, TextBox, PushButton #, Slider, Combo, CheckBox, ButtonGroup, info, warn
import time
import cv2
from PIL import Image
import json
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")
'''
employees = {}
employees['00001']={
    'name': 'Scott',
    'post': 'Engineer'
}
'''
with open('employee_data.txt', 'r') as outfile:
    employees = json.load(outfile)
    
def reset_c():
    global count, c
    count=0
    c=0
    #app.after(100,reset_c)
def get_data():
    pass

def loop():
    ret, frame = cap.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, +1)
    frame = Image.fromarray(frame)
    pic.value=frame
    app.update()
    #time.sleep(1)
    app.after(0,loop)
        
app = App(layout="grid",title = "Attendence")
btn_reset = PushButton(app, command =reset_c, text = "Reset",grid=[0,0])
btn_email = PushButton(app, command =reset_c, text = "Email",grid=[1,0])
btn_add_visitor = PushButton(app, command =reset_c, text = "Add Visitor",grid=[2,0])
#button = PushButton(app, command = counter_loop, text = "start loop")
#counter = Text(app,"0",grid = [0,1])
#counter2 = Text(app,"0",grid = [1,1])
pic = Picture(app,image = 'download.jpeg',width=300, height=300,grid =[0,2,3,3])
tv_name = Text(app,"Name: ",grid = [0,5],align='left')
tv_post = Text(app,"Post: ",grid = [0,6],align='left')
loop()
app.display()