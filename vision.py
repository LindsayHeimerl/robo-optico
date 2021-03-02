from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2


CLASSES = [
    'background',
    'aeroplane',
    'bicycle',
    'bird',
    'boat',
    'bottle',
    'bus',
    'car',
    'cat',
    'chair',
    'cow',
    'diningtable',
    'dog',
    'horse',
    'motorbike',
    'person',
    'pottedplant',
    'sheep',
    'sofa',
    'train',
    'tvmonitor'
]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe("./deploy.prototxt", "./MobileNetSSD_deploy.caffemodel")

print("[INFO] starting video stream...")
vs = VideoStream(src=0)

def StartVideo():
    global vs
    vs.start()

def StopVideo():
    global vs
    vs.stop()

def ReadFrame():
    global vs
    return vs.read()

def RunNeuralNetwork(frame):
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)),
        0.007843,
        (300, 300),
        127.5)

    net.setInput(blob)
    detections = net.forward()

    return detections

def FindHuman(frame, detections):
    (h, w) = frame.shape[0:2]

    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.6:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            (x0, y0, x1, y1) = box.astype("int")
            label = CLASSES[idx]

            if label == 'bottle':
                return ((x0 + x1) / 2, (y0 + y1) / 2)

    return None

def LabelObjects(frame, detections):
    (h, w) = frame.shape[0:2]
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.8:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

            (x0, y0, x1, y1) = box.astype("int")
            label = "{}: {:.2f}%".format(
                CLASSES[idx],
                confidence * 100)

            cv2.rectangle(
                frame,
                (x0, y0),
                (x1, y1),
                COLORS[idx],
                2)

            y = y0 - 15 if y0 - 15 > 15 else y0 + 15

            cv2.putText(
                frame,
                label,
                (x0, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                COLORS[idx],
                2)