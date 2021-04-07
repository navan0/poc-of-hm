"""By Navaneeth KT."""
import cv2
import dlib
import time
import math


class SpeedCamera(object):
    def __init__(self, video):
        self.video = cv2.VideoCapture(video)
        self.carCascade = cv2.CascadeClassifier('myhaar.xml')
        self.WIDTH = 1280
        self.HEIGHT = 720

    def estimateSpeed(self, location1, location2):
        d_pixels = math.sqrt(math.pow(
            location2[0] - location1[0], 2)
            + math.pow(location2[1] - location1[1], 2))
        ppm = 8.8
        d_meters = d_pixels / ppm
        fps = 18
        speed = d_meters * fps * 3.6
        return speed

    def get_frame(self):
        """
        Get the frame , find and draw the bbox in each frameand sent it
        the flask service as frames.
        """
        rc, image = self.video.read()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rectangleColor = (0, 255, 0)
        frameCounter = 0
        currentCarID = 0
        fps = 0
        carTracker = {}
        carLocation1 = {}
        carLocation2 = {}
        speed = [None] * 1000
        resultImage = image.copy()
        try:
            start_time = time.time()
            frameCounter = frameCounter + 1
            carIDtoDelete = []
            for carID in carTracker.keys():
                trackingQuality = carTracker[carID].update(image)
                if trackingQuality < 7:
                    carIDtoDelete.append(carID)
            for carID in carIDtoDelete:
                carTracker.pop(carID, None)
                carLocation1.pop(carID, None)
                carLocation2.pop(carID, None)
            if not (frameCounter % 10):
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                cars = self.carCascade.detectMultiScale(
                    gray, 1.1, 13, 18, (24, 24))
                for (_x, _y, _w, _h) in cars:
                    x = int(_x)
                    y = int(_y)
                    w = int(_w)
                    h = int(_h)
                    x_bar = x + 0.5 * w
                    y_bar = y + 0.5 * h
                    matchCarID = None
                    for carID in carTracker.keys():
                        trackedPosition = carTracker[carID].get_position()
                        t_x = int(trackedPosition.left())
                        t_y = int(trackedPosition.top())
                        t_w = int(trackedPosition.width())
                        t_h = int(trackedPosition.height())
                        t_x_bar = t_x + 0.5 * t_w
                        t_y_bar = t_y + 0.5 * t_h
                        if ((t_x <= x_bar <= (t_x + t_w)) and (t_y <= y_bar <= (t_y + t_h)) and (x <= t_x_bar <= (x + w)) and (y <= t_y_bar <= (y + h))):
                            matchCarID = carID
                    if matchCarID is None:
                        tracker = dlib.correlation_tracker()
                        tracker.start_track(image, dlib.rectangle(x, y, x + w, y + h))
                        carTracker[currentCarID] = tracker
                        carLocation1[currentCarID] = [x, y, w, h]
                        currentCarID = currentCarID + 1

            for carID in carTracker.keys():
                trackedPosition = carTracker[carID].get_position()
                t_x = int(trackedPosition.left())
                t_y = int(trackedPosition.top())
                t_w = int(trackedPosition.width())
                t_h = int(trackedPosition.height())
                cv2.rectangle(resultImage, (t_x, t_y), (t_x + t_w, t_y + t_h), rectangleColor, 4)
                carLocation2[carID] = [t_x, t_y, t_w, t_h]
            end_time = time.time()

            if not (end_time == start_time):
                fps = 1.0/(end_time - start_time)

            for i in carLocation1.keys():
                if frameCounter % 1 == 0:
                    [x1, y1, w1, h1] = carLocation1[i]
                    [x2, y2, w2, h2] = carLocation2[i]
                    carLocation1[i] = [x2, y2, w2, h2]
                    if [x1, y1, w1, h1] != [x2, y2, w2, h2]:
                        if (speed[i] == None or speed[i] == 0) and y1 >= 275 and y1 <= 285:
                            speed[i] = self.estimateSpeed([x1, y1, w1, h1], [x2, y2, w2, h2])
                        if speed[i] != None and y1 >= 180:
                            cv2.putText(resultImage, str(int(speed[i])) + " km/hr", (int(x1 + w1/2), int(y1-5)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        except:
            print("no mask is detecting")
        ret, jpeg = cv2.imencode('.png', image)
        ret1, jpeg1 = cv2.imencode('.png', gray)
        return (jpeg.tobytes(), jpeg1.tobytes())
