import cv2
import numpy as np
import time
import threading
import winsound
import json
import logging
from datetime import datetime
from line_follow import detect_parallel_lines
from obj_detect import is_obstacle_detected
from railway_config import *

class AdvancedRailwaySystem:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.obstacle_start_time = None
        self.buzzer_active = False
        self.railway_stopped = False
        self.emergency_stop_time = None
        self.system_start_time = time.time()
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Advanced features
        self.speed = 0  # km/h
        self.max_speed = 80  # km/h
        self.weather_condition = "Clear"
        self.track_condition = "Good"
        self.maintenance_due = False
        self.obstacle_history = []
        self.emergency_stops_count = 0
        
        # Initialize buzzer thread
        self.buzzer_thread = None
        self.stop_buzzer = False
        
        # Setup logging
        if ENABLE_LOGGING:
            logging.basicConfig(
                filename=LOG_FILE,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        
        # Load system state
        self.load_system_state()
        
    def load_system_state(self):
        """Load system state from file"""
        try:
            with open('railway_state.json', 'r') as f:
                state = json.load(f)
                self.emergency_stops_count = state.get('emergency_stops_count', 0)
                self.maintenance_due = state.get('maintenance_due', False)
        except FileNotFoundError:
            pass
    
    def save_system_state(self):
        """Save system state to file"""
        state = {
            'emergency_stops_count': self.emergency_stops_count,
            'maintenance_due': self.maintenance_due,
            'last_updated': datetime.now().isoformat()
        }
        with open('railway_state.json', 'w') as f:
            json.dump(state, f)
    
    def estimate_distance(self, frame, obstacle_bbox):
        """Enhanced distance estimation with multiple factors"""
        if obstacle_bbox is None:
            return float('inf')
            
        x1, y1, x2, y2 = obstacle_bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        bbox_area = bbox_width * bbox_height
        
        frame_area = FRAME_WIDTH * FRAME_HEIGHT
        relative_size = bbox_area / frame_area
        
        # Enhanced distance estimation
        if relative_size > DISTANCE_ESTIMATION["very_close"]:
            return 1.5
        elif relative_size > DISTANCE_ESTIMATION["close"]:
            return 3.0
        elif relative_size > DISTANCE_ESTIMATION["medium"]:
            return 6.0
        else:
            return 10.0
    
    def detect_weather_conditions(self, frame):
        """Detect weather conditions from camera feed"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Analyze brightness and contrast
        brightness = np.mean(hsv[:, :, 2])
        
        if brightness < 50:
            self.weather_condition = "Dark/Low Light"
        elif brightness > 200:
            self.weather_condition = "Bright"
        else:
            self.weather_condition = "Normal"
        
        return self.weather_condition
    
    def adjust_speed_based_on_conditions(self):
        """Adjust speed based on weather and track conditions"""
        base_speed = self.max_speed
        
        # Weather adjustments
        if self.weather_condition == "Dark/Low Light":
            base_speed *= 0.7
        elif self.weather_condition == "Bright":
            base_speed *= 0.9
        
        # Track condition adjustments
        if self.track_condition == "Poor":
            base_speed *= 0.5
        
        # Obstacle history adjustments
        if len(self.obstacle_history) > 5:
            base_speed *= 0.8
        
        self.speed = min(base_speed, self.max_speed)
        return self.speed
    
    def predict_maintenance_needs(self):
        """Predict maintenance needs based on system usage"""
        uptime_hours = (time.time() - self.system_start_time) / 3600
        
        if uptime_hours > 24:  # Daily maintenance check
            self.maintenance_due = True
        
        if self.emergency_stops_count > 10:  # Emergency stop threshold
            self.maintenance_due = True
        
        return self.maintenance_due
    
    def start_buzzer(self):
        """Enhanced buzzer with different patterns"""
        def buzzer_loop():
            while not self.stop_buzzer and self.buzzer_active:
                # Emergency pattern: faster beeps
                winsound.Beep(BUZZER_FREQUENCY, BUZZER_DURATION)
                time.sleep(BUZZER_PAUSE)
        
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
        """Enhanced emergency stop with logging"""
        self.railway_stopped = True
        self.emergency_stop_time = time.time()
        self.emergency_stops_count += 1
        self.stop_buzzer_sound()
        
        # Log emergency stop
        if ENABLE_LOGGING:
            logging.warning(f"EMERGENCY STOP: Railway stopped. Total stops: {self.emergency_stops_count}")
        
        print(f"🚨 EMERGENCY STOP: Railway stopped due to close obstacle!")
        print(f"📊 Total emergency stops: {self.emergency_stops_count}")
        
        self.save_system_state()
        return "EMERGENCY_STOP"
    
    def auto_restart_check(self):
        """Check if system should auto-restart after emergency stop"""
        if not AUTO_RESTART_ENABLED or self.emergency_stop_time is None:
            return False
        
        time_since_stop = time.time() - self.emergency_stop_time
        if time_since_stop > RESTART_DELAY:
            self.railway_stopped = False
            self.emergency_stop_time = None
            print("🔄 Auto-restarting railway system...")
            return True
        return False
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
        
        return self.fps_counter
    
    def run(self):
        """Main railway system loop with advanced features"""
        print("🚂 Advanced Railway Automatic System Started")
        print("Press 'q' to quit, 'r' to reset emergency stop, 'm' for maintenance info")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to read camera feed")
                break

            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            
            # Calculate FPS
            fps = self.calculate_fps()
            
            # Detect weather conditions
            weather = self.detect_weather_conditions(frame)
            
            # Check for auto-restart
            if self.railway_stopped:
                self.auto_restart_check()
            
            # 1. Check for obstacle
            obstacle_detected, frame, obstacle_bbox = is_obstacle_detected(frame)
            
            if obstacle_detected:
                # Estimate distance to obstacle
                distance = self.estimate_distance(frame, obstacle_bbox)
                
                # Store obstacle history
                self.obstacle_history.append({
                    'time': time.time(),
                    'distance': distance,
                    'weather': weather
                })
                
                # Keep only last 10 obstacles
                if len(self.obstacle_history) > 10:
                    self.obstacle_history.pop(0)
                
                # Check if obstacle is too close (less than 2 feet)
                if distance <= DISTANCE_THRESHOLD:
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
                    
                    # Start buzzer after threshold
                    if obstacle_duration >= OBSTACLE_DETECTION_THRESHOLD and not self.buzzer_active:
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
            
            # Adjust speed based on conditions
            current_speed = self.adjust_speed_based_on_conditions()
            
            # Check maintenance needs
            maintenance_needed = self.predict_maintenance_needs()
            
            # Display advanced information
            status_text = "🟢 RUNNING" if not self.railway_stopped else "🔴 STOPPED"
            cv2.putText(frame, f"Status: {status_text}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Speed: {current_speed:.1f} km/h", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"Weather: {weather}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, f"FPS: {fps}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if maintenance_needed:
                cv2.putText(frame, "MAINTENANCE DUE", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            cv2.imshow("Advanced Railway System", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r') and self.railway_stopped:
                self.railway_stopped = False
                self.emergency_stop_time = None
                print("🔄 Manual reset - Railway system restarted")
            elif key == ord('m'):
                self.show_maintenance_info()

        self.cap.release()
        cv2.destroyAllWindows()
        self.stop_buzzer_sound()
        self.save_system_state()
        print("🚂 Advanced Railway System Shutdown Complete")
    
    def show_maintenance_info(self):
        """Display maintenance information"""
        print("\n🔧 MAINTENANCE INFORMATION:")
        print(f"   Emergency Stops: {self.emergency_stops_count}")
        print(f"   System Uptime: {(time.time() - self.system_start_time) / 3600:.1f} hours")
        print(f"   Maintenance Due: {self.maintenance_due}")
        print(f"   Obstacle History: {len(self.obstacle_history)} recent detections")
        print(f"   Weather Condition: {self.weather_condition}")
        print(f"   Current Speed: {self.speed:.1f} km/h")
        print()

if __name__ == "__main__":
    railway_system = AdvancedRailwaySystem()
    railway_system.run() 