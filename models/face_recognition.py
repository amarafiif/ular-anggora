import cv2
import numpy as np
from PIL import Image
import os
from datetime import datetime

recognizer = cv2.face.LBPHFaceRecognizer_create()


def detect_faces(image):
    cascade_path = "cascades/haarcascade_frontalface_default.xml"
    if not os.path.exists(cascade_path):
        raise ValueError(f"Cascade file not found: {cascade_path}")

    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(
        image,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE,
    )
    return faces


def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    ids = []

    for image_path in image_paths:
        pil_image = Image.open(image_path).convert("L")  # Convert it to grayscale
        image_np = np.array(pil_image, "uint8")
        user_id = int(
            os.path.split(image_path)[-1].split(".")[1]
        )  # Assuming the filename starts with 'User.{id}.'
        faces = detect_faces(image_np)  # Detect faces using detect_faces function

        for x, y, w, h in faces:
            face_samples.append(image_np[y : y + h, x : x + w])
            ids.append(user_id)

    return face_samples, ids


def train_model():
    path = "dataset"
    face_samples, ids = get_images_and_labels(path)
    recognizer.train(face_samples, np.array(ids))
    if not os.path.exists("trainer"):
        os.makedirs("trainer")
    recognizer.write("trainer/trainer.yml")


def recognize_face(image_path):
    recognizer.read("trainer/trainer.yml")
    cascade_path = "cascades/haarcascade_frontalface_default.xml"
    if not os.path.exists(cascade_path):
        raise ValueError(f"Cascade file not found: {cascade_path}")
    face_cascade = cv2.CascadeClassifier(cascade_path)

    pil_image = Image.open(image_path).convert("L")  # Convert it to grayscale
    image_np = np.array(pil_image, "uint8")
    faces = face_cascade.detectMultiScale(image_np)

    for x, y, w, h in faces:
        id, confidence = recognizer.predict(image_np[y : y + h, x : x + w])
        return id, confidence

    return None, None


def save_image_with_label(image_path, user_id):
    if not os.path.exists("dataset"):
        os.makedirs("dataset")
    pil_image = Image.open(image_path).convert("L")  # Convert it to grayscale
    image_np = np.array(pil_image, "uint8")
    faces = detect_faces(image_np)  # Detect faces

    for x, y, w, h in faces:
        face = image_np[y : y + h, x : x + w]
        face_image = Image.fromarray(face)
        dataset_image_path = (
            f"dataset/User.{user_id}.{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        )
        face_image.save(dataset_image_path)
