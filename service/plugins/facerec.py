"""By Navaneeth KT."""

import os

import cv2
import face_recognition
import face_recognition as fr
import numpy as np


class FaceRec(object):
    """encode and classify faces in FaceRec."""

    def __init__(self, img):
        """Init."""
        self.img = img

    def get_encoded_faces(self):
        """Encode faces."""
        self.encoded = {}

        faces_dir = os.path.join(os.path.dirname(__file__), 'faces')

        for dirpath, dnames, fnames in os.walk(faces_dir):
            for f in fnames:
                if f.endswith(".jpg") or f.endswith(".png"):
                    face = fr.load_image_file(
                        os.path.join(faces_dir, f))
                    print(os.path.join(faces_dir, f))
                    encoding = fr.face_encodings(face)[0]
                    self.encoded[f.split(".")[0]] = encoding

        return self.encoded

    def classify_face(self):
        """Classify images."""
        faces = self.get_encoded_faces()
        faces_encoded = list(faces.values())
        known_face_names = list(faces.keys())
        img = cv2.imread(self.img, 1)
        face_locations = face_recognition.face_locations(img)
        unknown_face_encodings = face_recognition.face_encodings(
            img, face_locations)
        face_names = []
        for face_encoding in unknown_face_encodings:
            matches = face_recognition.compare_faces(
                faces_encoded, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(
                faces_encoded, face_encoding)
            print(face_distances)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            return face_names
