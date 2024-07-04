from flask import Flask, request, jsonify, render_template, Response
from models.face_recognition import (
    train_model,
    recognize_face,
    save_image_with_label,
    detect_faces,
)
from database.db import (
    init_db,
    add_user,
    get_user_name_by_id,
    get_user_id_by_name,
    update_user_image_path,
    get_user_nim_by_id,
    add_presence,
    get_user_info_by_id,
    get_user_image_path,
)
from datetime import datetime
import base64
import os
import cv2
from PIL import Image
import numpy as np
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
CORS(app)

recognizer = cv2.face.LBPHFaceRecognizer_create()
if os.path.exists("trainer/trainer.yml"):
    recognizer.read("trainer/trainer.yml")
attendance = []


@app.route("/")
def index():
    return render_template("index.html")


def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray)
            for x, y, w, h in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                user_id, confidence = recognizer.predict(gray[y : y + h, x : x + w])
                if confidence < 100:
                    name = get_user_name_by_id(user_id)
                    nim = get_user_nim_by_id(user_id)
                    label = f"{nim}_{name}"
                    color = (0, 255, 0) if confidence < 100 else (0, 0, 255)
                else:
                    label = "Unknown"
                    color = (0, 0, 255)
                cv2.putText(
                    frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2
                )
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/register", methods=["POST"])
def register():
    try:
        name = request.form["name"]
        kelas = request.form["kelas"]
        nim = request.form["nim"]
        image_data = request.form["image"]  # Ambil foto dari kamera web (base64)
        created_at = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        print(
            f"Received data: name={name}, kelas={kelas}, nim={nim}, created_at={created_at}"
        )

        # Decode base64 image data
        image_data = image_data.split(",")[
            1
        ]  # Remove the 'data:image/jpeg;base64,' part
        image_data = base64.b64decode(image_data)
        print("Image data decoded successfully")

        # Tambahkan data pengguna ke database
        add_user(name, "", kelas, nim, created_at)
        print("User added to database")

        # Ambil ID pengguna dari database
        user_id = get_user_id_by_name(name)
        print(f"User ID fetched from database: {user_id}")

        # Simpan foto ke direktori dengan ID pengguna
        image_path = f"static/images/{user_id}_{created_at}.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(image_data)

        print(f"Image saved to: {image_path}")

        # Update path gambar di database
        update_user_image_path(user_id, image_path)
        print("Image path updated in database")

        return jsonify({"message": "User registered successfully"})
    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/train", methods=["POST"])
def train():
    try:

        logging.debug("Request received to train endpoint")
        name = request.form["name"]
        logging.debug(f"Name received: {name}")
        user_id = get_user_id_by_name(name)
        if not user_id:
            return jsonify({"error": "User not found"}), 404

        # Ambil path gambar profil dari database atau langsung dari folder
        user_image_path = get_user_image_path(
            user_id
        )  # Panggil fungsi get_user_image_path
        if not user_image_path:
            return jsonify({"error": "User image not found"}), 404

        # Baca gambar profil dari path yang telah disimpan
        profile_image = cv2.imread(user_image_path)
        gray_profile = cv2.cvtColor(profile_image, cv2.COLOR_BGR2GRAY)

        # Inisialisasi kamera dan ambil 25 gambar dari kamera
        camera = cv2.VideoCapture(0)
        count = 0
        while count < 25:
            success, frame = camera.read()
            if not success:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detect_faces(gray_frame)
            for x, y, w, h in faces:
                count += 1
                face = gray_frame[y : y + h, x : x + w]
                # Simpan gambar ke dataset
                dataset_image_path = f"dataset/User.{user_id}.{count}.jpg"
                cv2.imwrite(dataset_image_path, face)
                if count >= 25:
                    break

        camera.release()
        train_model()  # Panggil fungsi untuk melatih model setelah semua gambar tersimpan

        return jsonify({"message": "Training completed with 25 images per user"})
    except Exception as e:
        print(f"Error during training: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/presensi", methods=["GET"])
def presensi_page():
    return render_template("presensi.html")


@app.route("/presensi", methods=["POST"])
def presensi():
    try:
        image_data = request.json.get("image")
        if not image_data:
            return jsonify({"error": "No image data provided"}), 400

        image_data = image_data.split(",")[
            1
        ]  # Remove the 'data:image/jpeg;base64,' part
        image_data = base64.b64decode(image_data)

        # Simpan gambar sementara
        image_path = "static/images/uploaded_image.jpg"
        with open(image_path, "wb") as img_file:
            img_file.write(image_data)

        user_id, confidence = recognize_face(image_path)
        if user_id is not None:
            user_info = get_user_info_by_id(user_id)
            if user_info:
                nim, name = user_info
                add_presence(nim, name)
                return jsonify(
                    {
                        "message": "Presence recorded successfully",
                        "nim": nim,
                        "name": name,
                    }
                )
            else:
                return jsonify({"error": "User information not found."}), 404
        else:
            return jsonify({"error": "No face detected."}), 400
    except Exception as e:
        print(f"Error during presence: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        file = request.files["image"]
        image_path = "static/images/uploaded_image.jpg"
        file.save(image_path)
        id, confidence = recognize_face(image_path)
        if id is not None:
            name = get_user_name_by_id(id)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            attendance.append(
                {
                    "id": id,
                    "name": name,
                    "kelas": "Kelas_placeholder",
                    "nim": "NIM_placeholder",
                    "confidence": confidence,
                    "timestamp": timestamp,
                }
            )
            return jsonify(
                {
                    "id": id,
                    "name": name,
                    "confidence": confidence,
                    "timestamp": timestamp,
                }
            )
        else:
            return jsonify({"error": "No face detected."}), 400
    except Exception as e:
        print(f"Error during recognition: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/attendance", methods=["GET"])
def show_attendance():
    return render_template("attendance.html", attendance=attendance)


if __name__ == "__main__":
    init_db()
    if not os.path.exists("static/images"):
        os.makedirs("static/images")
    app.run(debug=True)
