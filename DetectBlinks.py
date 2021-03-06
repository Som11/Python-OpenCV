'''

this code detects blinks in the eyes and displays the total number of blinks
either of the eyes or both eyes, when blinked, is detected
the net blink count is displayed on the output stream 


implement audio playback using:
##import os
##os.startfile('E:\\Data-Som\\Music\\BucketheadSoothsayer.wav')

##putting text onto the output stream
##cv.puttext(img, str(L), (x, y), font, 2, (0,0,0), 1)


'''
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import imutils
import time
from time import sleep
import dlib
import cv2
import os
from cv2 import *

#os.startfile('E:\\Data-Som\\Music\\BucketheadSoothsayer.wav')
print("Loading preferences..."); sleep(4)

def eye_aspect_ratio(eye):
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])
	# compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])
	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)
	# return the eye aspect ratio
	return ear

# define two constants, one for the eye aspect ratio to indicate blink and then a second constant for the number of consecutive frames the eye must be below the threshold
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3

# initialize the frame counters and the total number of blinks
COUNTER = 0
TOTAL = 0

# initialize dlib's face detector (HOG-based) and then create the facial landmark predictor
print("Loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')       

# grab the indexes of the facial landmarks for the left and right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("Initializing webcam for video stream thread...")
camera = VideoCapture(0)
time.sleep(1.0)

# loop over frames from the video stream
while True:
	ret, frame = camera.read()
	##frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# detect faces in the grayscale frame
	rects = detector(gray, 0)
	# loop over the face detections
	for rect in rects:
		# determine the facial landmarks for the face region, then convert the facial landmark (x, y)-coordinates to a NumPy array
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)
		# extract the left and right eye coordinates, then use the coordinates to compute the eye aspect ratio for both eyes
		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart:rEnd]
		leftEAR = eye_aspect_ratio(leftEye)
		rightEAR = eye_aspect_ratio(rightEye)
		# average the eye aspect ratio together for both eyes
		ear = (leftEAR + rightEAR) / 2.0
		# compute the convex hull for the left and right eye, then visualize each of the eyes
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)
		cv2.drawContours(frame, [leftEyeHull], -1, (255, 255, 0), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (255, 255, 0), 1)
		# check to see if the eye aspect ratio is below the blink threshold, and if so, increment the blink frame counter
		if ear < EYE_AR_THRESH:
			COUNTER += 1
		# otherwise, the eye aspect ratio is not below the blink threshold
		else:
			# if the eyes were closed for a sufficient number of then increment the total number of blinks
			if COUNTER >= EYE_AR_CONSEC_FRAMES:TOTAL += 1
			# reset the eye frame counter
			COUNTER = 0
			if TOTAL == 2:cv2.putText(frame, "Hello!", (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
		# draw the total number of blinks on the frame along with the computed eye aspect ratio for the frame
		cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
		cv2.putText(frame, "EAR: {:.2f}".format(ear), (500, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 0, 20), 2)
		
	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(30)
	if key !=-1:
		break

cv2.destroyAllWindows()
camera.release()
