import vision
import cv2
from flask import Flask, escape, request, Response
import imutils
import numpy as np


def generate():
    while True:
        frame = vision.ReadFrame()
        frame = imutils.resize(frame, width=400)
        (h, w) = frame.shape[0:2]

        detections = vision.ProcessFrame(frame)

        for i in np.arange(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.8:
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])

                (startX, startY, endX, endY) = box.astype("int")
                label = "{}: {:.2f}%".format(vision.CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    vision.COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, vision.COLORS[idx], 2)
                    # show the output frame

        (flag, encodedImage) = cv2.imencode(".jpg", frame)

        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + \
            bytearray(encodedImage) + \
            b'\r\n'


app = Flask(__name__)
@app.route("/video_feed")
def video_feed():
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

vision.StartVideo()

app.run(host='0.0.0.0')

vision.StopVideo()
