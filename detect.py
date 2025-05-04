import cv2
from ultralytics import YOLO
import ollama

# Load YOLOv5 model
model = YOLO('model/yolov5s.pt')

def detect_violence_in_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(rgb, imgsz=640)

    found_violence = False
    detected_objects = []

    # Handle both single or list results
    if isinstance(results, list):
        result = results[0]
    else:
        result = results

    if hasattr(result, 'boxes') and result.boxes is not None:
        boxes = result.boxes.xyxy
        confidences = result.boxes.conf
        class_ids = result.boxes.cls

        for box, conf, cls in zip(boxes, confidences, class_ids):
            label = model.names[int(cls)]
            if conf > 0.3:
                x1, y1, x2, y2 = map(int, box.tolist())

                # Check if the label is violent
                if label in ["knife", "gun", "weapon", "fight"]:
                    detected_objects.append(label.capitalize())
                    found_violence = True
                elif label == "person":
                    detected_objects.append("Person")
                    found_violence = True  # Optional: treat presence of people as violence indicator

                # Draw the bounding box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    return frame, detected_objects, found_violence

def analyze_with_ollama(prompt):
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    print(response)
    return response.get("message", {}).get("content", "Ollama response doesn't contain expected text.")
