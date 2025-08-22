

import advanced_railway_system

if __name__ == "__main__":
    system = advanced_railway_system.AdvancedRailwaySystem()
    system.run()
from ultralytics import YOLO
import os

model_path = os.path.join(os.path.dirname(__file__), "yolov8s.pt")
model = YOLO(model_path)