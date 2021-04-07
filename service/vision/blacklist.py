"""By Navaneeth KT."""
import glob
import os

import cv2
import face_recognition
import numpy as np


class BlaclistCamera(object):
    def __init__(self, video):
        self.video = cv2.VideoCapture(video)
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    def get_encode(self):
        self.dic = {}
        self.faces = glob.glob("blacklist/*")
        self.encoded = {}
        for face in self.faces:
            # import pdb; pdb.set_trace()
            name = os.path.basename(face)
            name = name.split(".")[0]
            face = face_recognition.load_image_file(face)
            encoding = face_recognition.face_encodings(face)[0]
            self.encoded[name.split(".")[0]] = encoding

        return self.encoded

    def get_frame(self):
        """
        Get the frame , find and draw the bbox in each frameand sent it the
        flask service as frames.
        """
        faces = self.get_encode()
        known_face_encodings = list(faces.values())
        known_face_names = list(faces.keys())
        ret, frame = self.video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        try:
            if self.process_this_frame:
                face_locations = face_recognition.face_locations(
                    rgb_small_frame)
                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame, face_locations)
                face_names = []
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                    face_names.append(name)
            self.process_this_frame = not self.process_this_frame
            for (top, right, bottom, left), name in zip(
                    face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                name = name.split('-')[-1]

                cv2.rectangle(
                    frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(
                    frame, (left, bottom - 35), (right, bottom), (0, 0, 255),
                    cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    frame, name, (left + 6, bottom - 6), font, 1.0,
                    (255, 255, 255), 1)
        except:
            print("no mask is detecting")
        ret, jpeg = cv2.imencode('.png', frame)
        ret1, jpeg1 = cv2.imencode('.png', gray)
        return (jpeg.tobytes(), jpeg1.tobytes())
