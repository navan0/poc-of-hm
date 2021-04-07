"""By Navaneeth KT."""
import math

import cv2
import imutils
import numpy as np


class SocialCamera(object):
    def __init__(self, video):
        self.confid = 0.5
        self.thresh = 0.5
        self.video = cv2.VideoCapture(video)
        self.labelsPath = "coco.names"
        self.LABELS = open(self.labelsPath).read().strip().split("\n")
        np.random.seed(42)
        self.weightsPath = "yolov3-tiny.weights"
        self.configPath = "yolov3-tiny.cfg"
        self.net = cv2.dnn.readNetFromDarknet(self.configPath, self.weightsPath)
        self.ln = self.net.getLayerNames()
        self.ln = [
            self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        (self.W, self.H) = (None, None)
        self.fl = 0
        self.q = 0

    def get_frame(self):
        """
        Get the frame , find and draw the bbox in each frameand sent it
        the flask service as frames.
        """
        (grabbed, frame) = self.video.read()
        # frame = imutils.resize(frame, width=400)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self.W is None or self.H is None:
            (H, W) = frame.shape[:2]
            q = W

        try:
            frame = frame[0:H, 200:q]
            (H, W) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416),
                                         swapRB=True, crop=False)
            self.net.setInput(blob)
            layerOutputs = self.net.forward(self.ln)

            boxes = []
            confidences = []
            classIDs = []
            for output in layerOutputs:
                for detection in output:
                    scores = detection[5:]
                    classID = np.argmax(scores)
                    confidence = scores[classID]
                    if self.LABELS[classID] == "person":
                        if confidence > self.confid:
                            box = detection[0:4] * np.array([W, H, W, H])
                            (centerX, centerY, width, height) = box.astype(
                                "int")

                            x = int(centerX - (width / 2))
                            y = int(centerY - (height / 2))

                            boxes.append([x, y, int(width), int(height)])
                            confidences.append(float(confidence))
                            classIDs.append(classID)
            idxs = cv2.dnn.NMSBoxes(
                boxes, confidences, self.confid, self.thresh)
            ind = []
            for i in range(0, len(classIDs)):
                if(classIDs[i] == 0):
                    ind.append(i)
            a = []
            b = []
            if len(idxs) > 0:
                for i in idxs.flatten():
                    (x, y) = (boxes[i][0], boxes[i][1])
                    (w, h) = (boxes[i][2], boxes[i][3])
                    a.append(x)
                    b.append(y)

            distance = []
            nsd = []
            for i in range(0, len(a)-1):
                for k in range(1, len(a)):
                    if(k == i):
                        break
                    else:
                        x_dist = (a[k] - a[i])
                        y_dist = (b[k] - b[i])
                        d = math.sqrt(x_dist * x_dist + y_dist * y_dist)
                        distance.append(d)
                        if(d <= 100):
                            nsd.append(i)
                            nsd.append(k)
                        nsd = list(dict.fromkeys(nsd))
                        print(nsd)
            color = (0, 0, 255)
            for i in nsd:
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                center = [int(x + w / 2), int(y + h / 2)]
                center = (center[0], center[1])
                cv2.circle(frame, center, 1, (255, 0, 0), 2)
                text = "Alert"
                cv2.putText(
                    frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    color, 2)
            color = (0, 255, 0)
            if len(idxs) > 0:
                for i in idxs.flatten():
                    if (i in nsd):
                        break
                    else:
                        (x, y) = (boxes[i][0], boxes[i][1])
                        (w, h) = (boxes[i][2], boxes[i][3])
                        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                        text = 'Safe'
                        cv2.putText(
                            frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, color, 2)

        except:
            print("no mask is detecting")
        ret, jpeg = cv2.imencode('.png', frame)
        ret1, jpeg1 = cv2.imencode('.png', gray)
        return (jpeg.tobytes(), jpeg1.tobytes())
