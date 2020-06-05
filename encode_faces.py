from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images('photos'))
# initialize the list of known encodings and known names
knownEncodings = []
knownNames = []

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1,
        len(imagePaths)))
    name = imagePath.split(os.path.sep)[-2]
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
    for encoding in encodings:
        # add each encoding + name to our set of known names and
        # encodings
        knownEncodings.append(encoding)
        knownNames.append(name)
# dump the facial encodings + names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
f = open('encodings.pickle', "wb")
f.write(pickle.dumps(data))
f.close()