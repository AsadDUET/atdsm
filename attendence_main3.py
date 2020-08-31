from guizero import App , Picture, Text, TextBox, PushButton #, Slider, Combo, CheckBox, ButtonGroup, info, warn
import time
import cv2
from PIL import Image
import json
import test_face_rec as face
import scan_qr
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
camera = PiCamera()
camera.resolution = (640, 640)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 640))
time.sleep(0.1)
# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")
#cap.release()
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
    pass
    #app.after(100,reset_c)
def get_data():
    pass

def loop():
    global cap
    a = datetime.now()
    camera.capture(rawCapture, format="rgb",use_video_port=True)
    pi_image = rawCapture.array
    ids = scan_qr.scan(pi_image)
    if ids is not None:
        timer=time.perf_counter()
        print(ids)
        #cap = cv2.VideoCapture(0)
        identified=False
        while True:
            ret, frame = cap.read()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_width = frame.shape[1]
            #tv_post.value = ids
            for (x,y,w,h) in faces:
                forehead = (int(x+w/2),int(y+h*.15))
                frame = cv2.rectangle(frame,forehead,(forehead[0]+1,forehead[1]+1),(255,0,0),2)
                #frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                frame = cv2.rectangle(frame,((int(frame_width/2)-10),0),(int(frame_width/2+10),frame_width),(255,0,0),2)
                if abs(forehead[0]-frame_width/2)<20:
                    try:
                        names = face.detect(frame,faces)
                        tv_name.value = employees[names[0]]['name']
                        tv_post.value = employees[names[0]]['post']
                        if names[0]!='Unknown':
                            identified=True
                    except:
                        pass
                #frame = cv2.putText(frame,employees[names[0]]['name'],(x,y),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 0),2, cv2.LINE_AA)
                #roi_gray = gray[y:y+h, x:x+w]
                #roi_color = frame[y:y+h, x:x+w]
           
            frame = cv2.flip(frame, +1)
            frame = Image.fromarray(frame)
            pic.value=frame
            if (time.perf_counter()-timer)>10 or identified:
                cap.release()
                identified=False
                cap = cv2.VideoCapture(0)
                break
            app.update()
            
    pi_image = cv2.flip(pi_image, +1)
    pi_image = Image.fromarray(pi_image)
    qr_view.value = pi_image
    app.update()
    print(datetime.now()-a)
    rawCapture.truncate(0)
    app.after(1,loop)
        
app = App(layout="grid",title = "Attendence")
btn_reset = PushButton(app, command =reset_c, text = "Close",grid=[0,0])
btn_email = PushButton(app, command =reset_c, text = "Email",grid=[1,0])
btn_add_visitor = PushButton(app, command =reset_c, text = "Add Visitor",grid=[2,0])
#button = PushButton(app, command = counter_loop, text = "start loop")
#counter = Text(app,"0",grid = [0,1])
#counter2 = Text(app,"0",grid = [1,1])
pic = Picture(app,image = 'logo.jpeg',width=200, height=200,grid =[0,2,3,3])
qr_view = Picture(app,image = 'logo.jpeg',width=200, height=200,grid =[4,2,3,3])

Text(app,"Name: ",grid = [0,5],align='left')
Text(app,"Post: ",grid = [0,6],align='left')
tv_name = Text(app,"-",grid = [1,5],align='left')
tv_post = Text(app,"-",grid = [1,6],align='left')
loop()
app.display()