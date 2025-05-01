import cv2
import torch
import os
from ultralytics import YOLO
import ollama

# Load the local YOLOv5 model (adjust based on your model name)
model = YOLO('model/yolov5s.pt')  # Ensure the correct model path

# Detect violence in a frame (detecting people, weapons, and fighting actions)
def detect_violence_in_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(rgb, imgsz=640)  # Correct argument here (use 'imgsz')

    found_violence = False
    detected_objects = []

    # Print the structure of results to debug
    print("Results:", results)

    # In YOLOv5 or YOLOv8, results are usually in the form of a list of predictions
    if isinstance(results, list) and len(results) > 0:
        result = results[0]  # Get the first (or only) result
        
        # Extract bounding boxes (xyxy), confidences, and class labels
        if hasattr(result, 'boxes') and result.boxes is not None:
            boxes = result.boxes.xyxy  # Bounding box coordinates
            confidences = result.boxes.conf  # Confidence values
            class_ids = result.boxes.cls  # Class IDs for each object

            for box, conf, cls in zip(boxes, confidences, class_ids):
                label = model.names[int(cls)]  # Get class label for the detected object
                if conf > 0.3:  # You can adjust confidence threshold
                    x1, y1, x2, y2 = map(int, box)
                    if label == "person":
                        detected_objects.append('Person')
                        found_violence = True
                    elif label in ["knife", "gun", "weapon"]:  # Add weapon classes here
                        detected_objects.append(label)
                        found_violence = True
                    elif label == "fight":  # If you have a fight class in your model
                        detected_objects.append('Fight')
                        found_violence = True

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    return frame, detected_objects, found_violence

# Download video from YouTube
def download_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
    path = os.path.join("videos", f"{yt.title}.mp4")
    stream.download(output_path="videos", filename=f"{yt.title}.mp4")
    return path

# Function to analyze text with Ollama
def analyze_with_ollama(prompt):
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    
    # Debugging: print the response to check its structure
    print(response)  # This will help us understand the actual structure of the response
    
    # If response is structured as expected, extract the 'text' field
    if 'text' in response:
        return response['text']
    else:
        # Handle the case where the response doesn't contain the 'text' field
        return "Ollama response doesn't contain expected text."
