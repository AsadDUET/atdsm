from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.popup import Popup
import io
from time import sleep
import time
import cv2
#from PIL import Image as Pilimage
import json
import face_rec as face
import scan_qr
from datetime import datetime
from picamera.array import PiRGBArray
from picamera import PiCamera
import pickle
import encode_faces
import csv
import sendMail
Window.fullscreen=True
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(1)
cap.set(3,400)
cap.set(4,400)
camera = PiCamera()
camera.resolution = (400, 400)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(400, 400))

if not cap.isOpened():
    raise IOError("Cannot open webcam")
with open('employee_data.txt', 'r') as f:
    employees = json.load(f)
data = pickle.loads(open('database.pickle', "rb").read())
qr=None
home_loop=None
add_loop=None
class Email(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def s_email(self):
        sendMail.send('mycontacts.txt','message.txt',"message.txt","20200830")
    def ch_p_home(self):
        global home_loop, cap
        my_app.screen_manager.current='Home'
        home_loop=Clock.schedule_interval(my_app.home_page.loop,0)
class AddEmployee(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def ch_p_home(self):
        global home_loop, cap,add_loop
        Clock.unschedule(add_loop)
        my_app.screen_manager.current='Home'
        
        home_loop=Clock.schedule_interval(my_app.home_page.loop,0)
        #cap.release()
        #cap = cv2.VideoCapture(1)
    def add_employee_loop(self,dt):
        global cap
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,-1)
        buf=frame.tostring()
        image_texture= Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='rgb')
        image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
        self.ids['facePreview'].texture =image_texture
    def add(self):
        global data,cap
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)        
        encode_faces.add_employee(frame,faces,self.ids['ID'].text,self.ids['name'].text,self.ids['post'].text)
        data = pickle.loads(open('database.pickle', "rb").read())
class HomePage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids['FaceCam'].source='3.jpeg'
        self.ids['QrCam'].source='logo.jpeg'
        self.start_home_loop()
    def close_app(self):
        global cap
        cap.release()
        my_app.get_running_app().stop()
    
    def loop(self,dt):
        global cap, qr,data
        a = datetime.now()
        if qr is None:
            rawCapture.truncate(0)
            camera.capture(rawCapture, format="rgb",use_video_port=True)
            pi_image = rawCapture.array
            qr = scan_qr.scan(pi_image)
            pi_image = cv2.flip(pi_image, -1)
            buf=pi_image.tostring()
            image_texture= Texture.create(size=(pi_image.shape[1],pi_image.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['QrCam'].texture =image_texture
            rawCapture.truncate(0)
        if qr is not None:
            timer=time.perf_counter()
            identified=False
            ret, frame = cap.read()
            frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_width = frame.shape[1]
            for (x,y,w,h) in faces:
                forehead = (int(x+w/2),int(y+h*.15))
                frame = cv2.rectangle(frame,forehead,(forehead[0]+1,forehead[1]+1),(255,0,0),2)
                #frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                frame = cv2.rectangle(frame,((int(frame_width/2)-10),0),(int(frame_width/2+10),frame_width),(255,0,0),2)
                if abs(forehead[0]-frame_width/2)<20:
                    try:
                        qr='0' #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<error
                        match = face.compare(data[qr]['encoding'],frame,faces)
                        print(match)
                        if match<0.5:
                            identified=True
                            self.ids['name'].text  = data[qr]['name']
                            self.ids['post'].text  = data[qr]['post']
                            with open(datetime.now().strftime('%Y%m%d')+'.csv', mode='a') as employee_file:
                                employee_writer = csv.writer(employee_file,lineterminator = '\n')
                                employee_writer.writerow([qr, datetime.now().strftime('%H:%M:%S'),match[0]])
                        
                            
                    except:
                        raise
            frame = cv2.flip(frame,-1)
            buf=frame.tostring()
            image_texture= Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['FaceCam'].texture =image_texture
            if (time.perf_counter()-timer)>10 or identified:
                self.ids['FaceCam'].texture =CoreImage('logo.jpeg').texture
                cap.release()
                identified=False
                cap = cv2.VideoCapture(1)
                cap.set(3,400)
                cap.set(4,400)
                qr=None
                print('[Attendence] Done')
        print(datetime.now()-a)
    
    def ch_p_add(self):
        global cap, add_loop
        self.stop_home_loop()
        my_app.screen_manager.current='Add Employee'
        cap.release()
        cap = cv2.VideoCapture(1)
        cap.set(3,400)
        cap.set(4,400)
        add_loop=Clock.schedule_interval(my_app.AddEmployee_page.add_employee_loop,0)
    def ch_p_email(self):
        self.stop_home_loop()
        my_app.screen_manager.current='email'

    def start_home_loop(self):
        global data, home_loop
        data=pickle.loads(open('database.pickle', "rb").read())
        home_loop=Clock.schedule_interval(self.loop,0)
    def stop_home_loop(self):
        global home_loop
        Clock.unschedule(home_loop)
     
class AtdApp(MDApp):
    def build(self):
        
        self.screen_manager = ScreenManager()
        
        self.home_page = HomePage()
        screen = Screen(name='Home')
        screen.add_widget(self.home_page)
        self.screen_manager.add_widget(screen)
        
        self.AddEmployee_page = AddEmployee()
        screen = Screen(name='Add Employee')
        screen.add_widget(self.AddEmployee_page)
        self.screen_manager.add_widget(screen)
        
        self.email_page = Email()
        screen = Screen(name='email')
        screen.add_widget(self.email_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager
    
    
if __name__ == "__main__":
    my_app = AtdApp()
    
    my_app.run()