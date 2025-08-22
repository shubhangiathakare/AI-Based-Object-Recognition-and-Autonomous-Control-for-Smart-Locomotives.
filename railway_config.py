# Railway Automatic System Configuration

# Timing Settings
OBSTACLE_DETECTION_THRESHOLD = 30  # seconds before buzzer activates
DISTANCE_THRESHOLD = 2.0  # feet - emergency stop distance
BUZZER_FREQUENCY = 1000  # Hz
BUZZER_DURATION = 500  # milliseconds
BUZZER_PAUSE = 0.1  # seconds between beeps

# Camera Settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
FPS = 30

# Detection Settings
CONFIDENCE_THRESHOLD = 0.5
DETECTION_CLASSES = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
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
]

# Distance Estimation Settings
DISTANCE_ESTIMATION = {
    "very_close": 0.3,  # relative size threshold
    "close": 0.2,
    "medium": 0.1,
    "far": 0.05
}

# Logging Settings
ENABLE_LOGGING = True
LOG_FILE = "railway_system.log"

# Safety Settings
EMERGENCY_STOP_ENABLED = True
AUTO_RESTART_ENABLED = False
RESTART_DELAY = 60  # seconds after emergency stop 