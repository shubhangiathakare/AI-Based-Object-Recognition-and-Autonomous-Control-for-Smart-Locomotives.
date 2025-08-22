import cv2
from ultralytics import YOLO

model = YOLO("yolov8s.pt")  # Or use "yolov8s.pt" for more accuracy

def is_obstacle_detected(frame, conf_threshold=0.5):
    results = model(frame, verbose=False)[0]
    obstacle_bbox = None
    
    for result in results.boxes.data.tolist():
        x1, y1, x2, y2, score, cls_id = result
        if score > conf_threshold:
            cls_name = model.names[int(cls_id)]

            if cls_name in ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
                            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
                            "bird", "cat", "dog", "horse", "sheep", "cow",
                            "elephant", "bear", "zebra", "giraffe",
                            "backpack", "umbrella", "handbag", "tie", "suitcase",
                            "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
                            "skateboard", "surfboard", "tennis racket",
                            "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl",
                            "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
                            "chair", "sofa", "pottedplant", "bed", "dining table", "toilet", "tvmonitor", "laptop", "mouse", "remote",
                            "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
                            "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
            ]:
                # Draw bounding box
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                cv2.putText(frame, f"{cls_name} ({score:.2f})", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Store the largest detected obstacle for distance estimation
                if obstacle_bbox is None:
                    obstacle_bbox = (int(x1), int(y1), int(x2), int(y2))
                else:
                    # Keep the largest bounding box
                    current_area = (int(x2) - int(x1)) * (int(y2) - int(y1))
                    existing_area = (obstacle_bbox[2] - obstacle_bbox[0]) * (obstacle_bbox[3] - obstacle_bbox[1])
                    if current_area > existing_area:
                        obstacle_bbox = (int(x1), int(y1), int(x2), int(y2))
                
                return True, frame, obstacle_bbox
    
    return False, frame, obstacle_bbox
