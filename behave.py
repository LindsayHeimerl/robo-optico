import vision
import cv2
from flask import Flask, escape, request, Response
import imutils
import numpy as np
import time
import threading
import robot

frame_lock = threading.Lock()
frame = None
detections = None
position = None
pos_lock = threading.Lock()

def VisionThread():
    global frame
    global detections
    global position

    vision.StartVideo()

    while True:
        with frame_lock:
            frame = vision.ReadFrame()
            frame = imutils.resize(frame, width=400)
        detections = vision.RunNeuralNetwork(frame)

        with pos_lock:
            position = vision.FindHuman(frame, detections)

        if position is not None:
            print(position)

def BehaviorThread():
    state = 'start'
    do_ram = True # For Lindsay's sake

    def Transition(to, stop_motors=True):
        print('{} -> {}'.format(state, to))
        if stop_motors:
            robot.SetMotors(0, 0)
        return to

    while True:
        time.sleep(0.1)
        with pos_lock:
            if state == 'start':
                if position is not None:
                    state = Transition('center-human')
                else:
                    time.sleep(0.1)
                    state = Transition('start')

            elif state == 'center-human':
                if position is None:
                    state = Transition('start')

                elif np.abs(position[0] - 200) < 10:
                    state = Transition('follow')

                elif position[0] > 200:
                    # To the right!
                    robot.SetMotors(0.2, -0.2)

                else:
                    # To the left, to the left
                    robot.SetMotors(-0.2, 0.2)

            elif state == 'follow':
                robot.SetMotors(0.5, 0.5)
                time.sleep(2)
                state = Transition('start')
                continue

                if position is None:
                    state = Transition('start')

                elif np.abs(position[0] - 200) > 10:
                    state = Transition('center-human')

                elif robot.QueryIrSensor() > 10:
                    robot.SetMotors(1.0, 1.0)

                elif not do_ram: # Distance < 10 cm
                    robot.SetMotors(0, 0)

            elif state == 'move-forward':
                if position is not None:
                    state = Transition('center-human')

                elif robot.QueryIrSensor() < 10:
                    state = Transition('turn')
                else:
                    robot.SetMotors(0.2, 0.2)

            elif state == 'turn':
                if np.random.randint(0, 1) == 0:
                    robot.SetMotors(0.2, -0.2)
                else:
                    robot.SetMotors(-0.2, 0.2)

                time.sleep(0.3)
                state = Transition('start')



def WebsiteThread():
    app = Flask(__name__)

    def generate():
        while True:
            time.sleep(0.2)
            with frame_lock:
                img = frame.copy()

            vision.LabelObjects(img, detections)
            (flag, encodedImage) = cv2.imencode(".jpg", img)

            yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + \
                bytearray(encodedImage) + \
                b'\r\n'

    @app.route("/video_feed")
    def video_feed():
        return Response(generate(),
            mimetype = "multipart/x-mixed-replace; boundary=frame")

    app.run(host='0.0.0.0')

vision_thread = threading.Thread(target=VisionThread)
vision_thread.start()

behvaior_thread = threading.Thread(target=BehaviorThread)
behvaior_thread.start()

# website_thread = threading.Thread(target=WebsiteThread)
# website_thread.start()

vision_thread.join()
behvaior_thread.join()
# website_thread.join()
