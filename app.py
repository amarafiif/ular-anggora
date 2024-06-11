from flask import Flask, request, jsonify, render_template
from models.face_recognition import train_model, recognize_face, save_image_with_label
from database.db import (
    init_db,
    add_user,
    get_user_name_by_id,
    get_user_id_by_name,
    update_user_image_path,
)
from datetime import datetime
import base64
import os

app = Flask(__name__)

attendance = []


@app.route("/")
def index():
    return render_template("index.html")


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

        save_image_with_label(image_path, user_id)

        # Update path gambar di database
        update_user_image_path(user_id, image_path)
        print("Image path updated in database")

        # Lakukan training model dengan foto baru
        train_model()
        print("Model trained successfully")

        return jsonify({"message": "User registered successfully"})
    except Exception as e:
        print(f"Error during registration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/train", methods=["POST"])
def train():
    try:
        train_model()
        return jsonify({"message": "Training completed"})
    except Exception as e:
        print(f"Error during training: {e}")
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
