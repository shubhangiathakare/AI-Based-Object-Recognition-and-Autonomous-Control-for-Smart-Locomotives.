import cv2
import numpy as np
import time
import threading
import winsound
from line_follow import detect_parallel_lines
from obj_detect import is_obstacle_detected

class RailwayAutomaticSystem:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.obstacle_start_time = None
        self.buzzer_active = False
        self.railway_stopped = False
        self.obstacle_detection_threshold = 30  # seconds
        self.distance_threshold = 2  # feet (estimated from camera)
        self.fps = 30
        self.frame_width = 640
        self.frame_height = 480
        
        # Initialize buzzer thread
        self.buzzer_thread = None
        self.stop_buzzer = False
        
    def estimate_distance(self, frame, obstacle_bbox):
        """Estimate distance to obstacle using bounding box size"""
        if obstacle_bbox is None:
            return float('inf')
            
        x1, y1, x2, y2 = obstacle_bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_area = bbox_width * bbox_height
        
        # Simple distance estimation based on object size
        # Larger objects appear closer
        frame_area = self.frame_width * self.frame_height
        relative_size = bbox_area / frame_area
        
        # Rough estimation: larger relative size = closer distance
        if relative_size > 0.3:  # Very close (less than 2 feet)
            return 1.5
        elif relative_size > 0.2:  # Close (2-4 feet)
            return 3.0
        elif relative_size > 0.1:  # Medium (4-8 feet)
            return 6.0
        else:  # Far (more than 8 feet)
            return 10.0
    
    def start_buzzer(self):
        """Start buzzer in a separate thread"""
        def buzzer_loop():
            while not self.stop_buzzer and self.buzzer_active:
                # Play buzzer sound (frequency: 1000Hz, duration: 500ms)
                winsound.Beep(1000, 500)
                time.sleep(0.1)  # Small pause between beeps
        
        self.buzzer_thread = threading.Thread(target=buzzer_loop)
        self.buzzer_thread.daemon = True
        self.buzzer_thread.start()
    
    def stop_buzzer_sound(self):
        """Stop the buzzer"""
        self.buzzer_active = False
        self.stop_buzzer = True
        if self.buzzer_thread and self.buzzer_thread.is_alive():
            self.buzzer_thread.join(timeout=1)
    
    def emergency_stop(self):
        """Emergency stop procedure"""
        self.railway_stopped = True
        self.stop_buzzer_sound()
        print("🚨 EMERGENCY STOP: Railway stopped due to close obstacle!")
        return "EMERGENCY_STOP"
    
    def run(self):
        """Main railway system loop"""
        print("🚂 Railway Automatic System Started")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to read camera feed")
                break

            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            # 1. Check for obstacle
            obstacle_detected, frame, obstacle_bbox = is_obstacle_detected(frame)
            
            if obstacle_detected:
                # Estimate distance to obstacle
                distance = self.estimate_distance(frame, obstacle_bbox)
                
                # Check if obstacle is too close (less than 2 feet)
                if distance <= self.distance_threshold:
                    status = self.emergency_stop()
                    cv2.putText(frame, f"EMERGENCY STOP! Distance: {distance:.1f}ft", 
                               (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
                    cv2.putText(frame, "Railway Stopped - Buzzer Off", 
                               (10, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                else:
                    # Start timing if obstacle detected
                    if self.obstacle_start_time is None:
                        self.obstacle_start_time = time.time()
                        print(f"⚠️ Obstacle detected at distance: {distance:.1f}ft")
                    
                    # Calculate time obstacle has been detected
                    obstacle_duration = time.time() - self.obstacle_start_time
                    
                    # Start buzzer after 30 seconds
                    if obstacle_duration >= self.obstacle_detection_threshold and not self.buzzer_active:
                        self.buzzer_active = True
                        self.stop_buzzer = False
                        self.start_buzzer()
                        print(f"🚨 BUZZER ACTIVATED! Obstacle detected for {obstacle_duration:.1f} seconds")
                    
                    # Display information
                    cv2.putText(frame, f"Obstacle: {distance:.1f}ft - {obstacle_duration:.1f}s", 
                               (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    if self.buzzer_active:
                        cv2.putText(frame, "BUZZER: ON", (10, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                    
                    print(f"⚠️ Obstacle detected. Distance: {distance:.1f}ft, Duration: {obstacle_duration:.1f}s")
            else:
                # Reset obstacle timing when no obstacle detected
                if self.obstacle_start_time is not None:
                    print("✅ Obstacle cleared - resuming normal operation")
                    self.obstacle_start_time = None
                    self.stop_buzzer_sound()
                
                # Only do line following if railway is not stopped
                if not self.railway_stopped:
                    frame, direction = detect_parallel_lines(frame)
                    cv2.putText(frame, f"Direction: {direction}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    print(f"Direction: {direction}")
                else:
                    cv2.putText(frame, "Railway Stopped - Manual Reset Required", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            
            # Display system status
            status_text = "🟢 RUNNING" if not self.railway_stopped else "🔴 STOPPED"
            cv2.putText(frame, f"Status: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Railway Automatic System", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
        self.stop_buzzer_sound()
        print("🚂 Railway System Shutdown Complete")

if __name__ == "__main__":
    railway_system = RailwayAutomaticSystem()
    railway_system.run() 