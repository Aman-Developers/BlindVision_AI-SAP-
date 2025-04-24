from flask import Flask, request, jsonify, Response
import cv2
import torch
import numpy as np
import pyttsx3
import threading

app = Flask(__name__)

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
engine = pyttsx3.init()
engine.setProperty('rate', 150)

@app.route('/detect', methods=['POST'])
def detect():
    print("🟡 DETECT endpoint hit!")

    if 'image' not in request.files:
        print("🔴 No image uploaded!")
        return jsonify({"error": "No image uploaded"}), 400

    print("🟢 Image received, processing...")

    file = request.files['image']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    results = model(img)
    labels = results.pandas().xyxy[0]['name'].tolist()
    unique_labels = list(set(labels))

    print(f"[INFO] Detected: {unique_labels}")

    # ✅ Speak using fresh TTS engine to avoid RuntimeError
    # for label in unique_labels:
    #     print(f"[VOICE] Speaking: {label}")
    #     threading.Thread(target=speak_label, args=(label,)).start() FOR VOICE FROM BACKENDD

    return jsonify({"detected_objects": unique_labels}), 200

def speak_label(label):
    try:
        engine = pyttsx3.init()
        engine.say(label)
        engine.runAndWait()
        engine.stop()
    except RuntimeError as e:
        print(f"[ERROR] Voice error: {e}")

@app.route('/stream')
def stream():
    def generate():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            annotated = results.render()[0]
            _, buffer = cv2.imencode('.jpg', annotated)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        cap.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
