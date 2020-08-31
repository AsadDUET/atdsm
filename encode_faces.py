from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os




def folder_load():
    global face_cascade, knownEncodings,knownIDs,data
    # grab the paths to the input images in our dataset
    print("[INFO] quantifying faces...")
    imagePaths = list(paths.list_images('photos'))
    # initialize the list of known encodings and known ids
    
    print(knownIDs)
    # loop over the image paths
    for (i, imagePath) in enumerate(imagePaths):
            
        # extract the person ID from the image path

        ID = imagePath.split(os.path.sep)[-2]
        if ID not in knownIDs:
            print("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
            # load the input image and convert it from BGR (OpenCV ordering)
            # to dlib ordering (RGB)
            frame = cv2.imread(imagePath)
            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            #boxes = face_recognition.face_locations(rgb,model='hog')
            # compute the facial embedding for the face
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)
            # loop over the encodings
            print('[loopp-in-]',ID)
            for encoding in encodings:
                # add each encoding + ID to our set of known ids and
                # encodings
                knownEncodings.append(encoding)
                knownIDs.append(ID)
    # dump the facial encodings + ids to disk
    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "ids": knownIDs}
    print(data['ids'])
    f = open('encodings.pickle', "wb")
    f.write(pickle.dumps(data))
    f.close()
def add_employee(frame,faces,ID,name,post):
    data = pickle.loads(open('database.pickle', "rb").read())
    big_face_box=0
    for i,face in enumerate(faces):
        try:
            if face[2]>faces[i+1][2]:
                big_face_box=i
        except:
            pass
    print('face in:',frame)
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in faces]
    # compute the facial embedding for the face
    encodings = face_recognition.face_encodings(frame, boxes)
    data[ID]={}
    data[ID]['name']=name
    data[ID]['post']=post
    data[ID]["encoding"]=encodings[big_face_box]
    print(data)
    try:
        with open('database.pickle', "wb") as f:
            f.write(pickle.dumps(data))
            #f.close()
        data = pickle.loads(open('database.pickle', "rb").read())
    except:
        print('fail to save')
    
if __name__=='__main__':
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    knownEncodings = []
    knownIDs = []
    knownPosts = []
    knownNames=[]
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        

        cv2.imshow('Preview',frame)
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            print(faces)
            cap.release()
            cv2.destroyAllWindows()
            name=input('Name: ')
            post=input('Post: ')
            ID=input('ID: ')
            add_employee(frame,faces,ID,name,post)
            break
    
