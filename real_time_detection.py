import cv2
import torch
import pyttsx3

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Load YOLOv5
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
important_labels = ['person', 'car', 'bus', 'motorcycle', 'chair', 'bench', 'truck','door','wall', 'glass','table','stairs']

# Start webcam
cap = cv2.VideoCapture(0)
last_spoken = set()

print("Press 'q' to stop")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_height, frame_width = frame.shape[:2]
    results = model(frame)
    annotated_frame = results.render()[0]
    boxes = results.pred[0]  # (x1, y1, x2, y2, conf, class)

    current_objects = set()

    for *xyxy, conf, cls in boxes:
        class_id = int(cls.item())
        label = results.names[class_id]

        # Skip if not important
        if label not in important_labels:
            continue

        x1, y1, x2, y2 = map(int, xyxy)
        box_width = x2 - x1
        box_height = y2 - y1
        box_area = box_width * box_height
        total_area = frame_width * frame_height
        area_ratio = box_area / total_area

        # Distance estimation
        if area_ratio > 0.12:
            distance = "very close"
        elif area_ratio > 0.06:
            distance = "near"
        else:
            distance = "far"

        # Direction estimation
        center_x = (x1 + x2) // 2
        if center_x < frame_width / 3:
            direction = "on your left"
        elif center_x > 2 * frame_width / 3:
            direction = "on your right"
        else:
            direction = "in front"

        # ⚠️ Special warning alert
        if distance == "very close":
            sentence = f"⚠️ Warning! {label} very close {direction}"
        else:
            sentence = f"{label} {distance} {direction}"

        current_objects.add(sentence)

    # Say new objects
    new_objects = current_objects - last_spoken
    for obj in new_objects:
        engine.say(obj)
        engine.runAndWait()

    last_spoken = current_objects

    # Show result
    cv2.imshow('Smart Assist (Filtered & Alerts)', annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows() 