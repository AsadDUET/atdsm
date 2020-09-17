# import os
# os.environ['KIVY_AUDIO'] = 'sdl2'
from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
import io
import serial
from time import sleep
import time
import cv2
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
from pygame import mixer
mixer.init()

Window.size = (800, 480)
Window.fullscreen=True
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser.flush()
cam_no=1
cap = cv2.VideoCapture(cam_no)
cap.set(3,400)
cap.set(4,400)

try:
    #cap = cv2.VideoCapture(cam_no)
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
except:
    cam_no=0
print('cam no: ' ,cam_no)
cap.release()
cap = cv2.VideoCapture(cam_no)
cap.set(3,400)
cap.set(4,400)
camera = PiCamera()
camera.resolution = (400, 400)
camera.rotation = 180
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(400, 400))
# sound_complete = SoundLoader.load('sound/check_in_complete.wav')
# sound_complete.seek(0)
# print(sound_complete)
if not cap.isOpened():
    print("Cannot open webcam")
with open('employee_data.txt', 'r') as f:
    employees = json.load(f)
data = pickle.loads(open('database.pickle', "rb").read())
qr=None
home_loop=None
add_loop=None
timer=time.perf_counter()
class Email(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='email'
    def s_email(self):
        sendMail.send('mycontacts.txt','message.txt',"message.txt","20200830")
    def ch_p_home(self):
        global home_loop, cap
        my_app.screen_manager.current='Home'
class AddEmployee(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name='Add Employee'
    def ch_p_home(self):
        global home_loop, cap
        my_app.screen_manager.current='Home'
    def add_employee_loop(self,dt):
        global cap
        ret, frame = cap.read()
        # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(line)
        if len(faces)==0:
            ser.write(str('0').encode('utf-8'))
        for (x,y,w,h) in faces:

            forehead = (int(x+w/2),int(y+h*.15))
            frame = cv2.rectangle(frame,forehead,(forehead[0]+5,forehead[1]+5),(255,0,0),2)
            ser.write(str(int(frame.shape[0]/2-forehead[1])).encode('utf-8'))
            self.ids.forhead_pos.text=str(int(frame.shape[0]/2-forehead[1]))
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
    def on_enter(self):
        global add_loop, cap, cam_no
        print('Entered Add')
        add_loop=Clock.schedule_interval(self.add_employee_loop,0)
        # cap.release()
        # cap = cv2.VideoCapture(cam_no)
        # cap.set(3,400)
        # cap.set(4,400)
    def on_pre_leave(self):
        global add_loop
        Clock.unschedule(add_loop)
        print('Leaving Add')
class HomePage(MDScreen):
    def __init__(self, **kwargs):
        global home_loop
        super().__init__(**kwargs)
        self.name='Home'
        self.ids['FaceCam'].source='logo.jpeg'
        # self.ids['QrCam'].source='logo.jpeg'

        # self.menu_items = [{'viewclass': 'MDMenuItem',
        #                 'text': 'clickable item',}]
        # self.menu = MDDropdownMenu(
        #     items=self.menu_items,
        #     caller=self.ids.toolbar,
        #     width_mult=4)
        # self.menu.bind(on_press=self.menu_callback)
        # home_loop=Clock.schedule_interval(self.loop,0)
    # def myMenu(self):
    #     global home_loop
    #     # Clock.unschedule(home_loop)
    #     self.menu.open()
    # def menu_callback(self,*args):
    #     print(args[0])

    def close_app(self):
        global cap
        cap.release()
        my_app.get_running_app().stop()

    def loop(self,dt):
        global cap, qr,data,timer,cam_no
        a = datetime.now()
        if qr is None:
            rawCapture.truncate(0)
            camera.capture(rawCapture, format="rgb",use_video_port=True)
            timer=time.perf_counter()
            pi_image = rawCapture.array
            qr = scan_qr.scan(pi_image)
            pi_image = cv2.flip(pi_image, -1)
            buf=pi_image.tostring()
            image_texture= Texture.create(size=(pi_image.shape[1],pi_image.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['FaceCam'].texture =image_texture
            # rawCapture.truncate(0)
        if qr is not None:
            identified=False
            ret, frame = cap.read()
            # frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_width = frame.shape[1]
            if len(faces)==0:
                print('forhead: 0')
            for (x,y,w,h) in faces:
                forehead = (int(x+w/2),int(y+h*.15))
                frame = cv2.rectangle(frame,forehead,(forehead[0]+1,forehead[1]+1),(255,0,0),2)
                print('forhead: {}'.format(forehead[1]))
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
                            # sound_complete.play()


                    except:
                        raise
            frame = cv2.flip(frame,-1)
            buf=frame.tostring()
            image_texture= Texture.create(size=(frame.shape[1],frame.shape[0]),colorfmt='rgb')
            image_texture.blit_buffer(buf,colorfmt='rgb',bufferfmt='ubyte')
            self.ids['FaceCam'].texture =image_texture
            if (time.perf_counter()-timer)>10 or identified:
                if identified:
                    mixer.music.load("sound/check_in_complete.mp3")
                    mixer.music.play()
                # else:
                    # mixer.music.load("sound/check_in_complete.mp3")
                    # mixer.music.play()
                # self.ids['FaceCam'].texture =CoreImage('logo.jpeg').texture
                cap.release()
                identified=False
                cap = cv2.VideoCapture(cam_no)
                cap.set(3,400)
                cap.set(4,400)
                qr=None
                print('[Attendence] Done')
        print(datetime.now()-a)

    def ch_p_add(self):
        global cap
        my_app.screen_manager.current='Add Employee'

    def ch_p_email(self):
        global cap
        my_app.screen_manager.current='email'
    def on_enter(self):
        global home_loop, cap,cam_no
        print('Entered Home')
        home_loop=Clock.schedule_interval(self.loop,0)
        cap.release()
        cap = cv2.VideoCapture(cam_no)
        cap.set(3,400)
        cap.set(4,400)
    def on_pre_leave(self):
        global home_loop
        Clock.unschedule(home_loop)
        print('Leaving Home')
class AtdCompletePage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class AtdApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):

        self.screen_manager = ScreenManager()

        self.home_page = HomePage()
        self.screen_manager.add_widget(self.home_page)

        self.AddEmployee_page = AddEmployee()
        self.screen_manager.add_widget(self.AddEmployee_page)

        self.email_page = Email()
        self.screen_manager.add_widget(self.email_page)

        self.atd_complete_page = AtdCompletePage()
        self.screen_manager.add_widget(self.atd_complete_page)

        return self.screen_manager

if __name__ == "__main__":
    my_app = AtdApp()

    my_app.run()
