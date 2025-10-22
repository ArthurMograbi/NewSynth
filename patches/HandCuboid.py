# patches/HandCuboid.py
import cv2
import mediapipe as mp
import numpy as np
import threading
from .VisualPatch import VisualPatch
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

class HandDetector:
    def __init__(self, 
                 static_image_mode=False,
                 max_num_hands=2,
                 min_detection_confidence=0.7,
                 min_tracking_confidence=0.4):
        
        self.config = {
            'static_image_mode': static_image_mode,
            'max_num_hands': max_num_hands,
            'min_detection_confidence': min_detection_confidence,
            'min_tracking_confidence': min_tracking_confidence
        }
        
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(**self.config)
        self.mp_draw = mp.solutions.drawing_utils
        
        self.results = None
        self.hand_landmarks_list = []
        self.key_landmarks_list = []
        
    def find_hands(self, img, draw=False):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        self.hand_landmarks_list = []
        self.key_landmarks_list = []
        
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
                landmark_positions = self._extract_landmark_positions(img, hand_landmarks)
                self.hand_landmarks_list.append(landmark_positions)
                
                key_landmarks = self._extract_key_landmarks(landmark_positions)
                self.key_landmarks_list.append(key_landmarks)
                
        return img
    
    def _extract_landmark_positions(self, img, hand_landmarks):
        landmark_list = []
        h, w, c = img.shape
        
        for id, landmark in enumerate(hand_landmarks.landmark):
            cx, cy = int(landmark.x * w), int(landmark.y * h)
            landmark_list.append([id, cx, cy])
            
        return landmark_list
    
    def _extract_key_landmarks(self, landmark_list):
        if not landmark_list:
            return None
            
        key_landmarks = {
            'pinky': landmark_list[20][1:],
            'ring': landmark_list[16][1:],
            'index': landmark_list[8][1:],
            'thumb': landmark_list[4][1:],
            'wrist': landmark_list[0][1:]
        }
        return key_landmarks
    
    @property
    def hand_count(self):
        return len(self.hand_landmarks_list)

class HandCuboid(VisualPatch):
    
    _metadata = {
        "io": {
            "cuboid_height": "out",
            "cuboid_width": "out",
            "cuboid_depth": "out",
            "cuboid_rotation_x": "out",
            "cuboid_rotation_y": "out",
            "cuboid_rotation_z": "out"
        }
    }

    def __init__(self):
        super().__init__()
        # Output parameters
        self.cuboid_height = 0.0
        self.cuboid_width = 0.0
        self.cuboid_depth = 0.0
        self.cuboid_rotation_x = 0.0
        self.cuboid_rotation_y = 0.0
        self.cuboid_rotation_z = 0.0
        
        # Hand tracking
        self.detector = HandDetector()
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.frame = None
        self.latest_data = None
        self.lock = threading.Lock()
        
        # Start hand tracking thread
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        # Create visual element
        self.visual_element = self._create_visual_element()
    
    def _create_visual_element(self):
        """Create the visual display for hand tracking"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setText("Hand Tracking Initializing...")
        
        self.data_label = QLabel()
        self.data_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.video_label)
        layout.addWidget(self.data_label)
        
        return widget
    
    def _tracking_loop(self):
        """Main hand tracking loop running in separate thread"""
        while self.running:
            success, img = self.cap.read()
            if not success:
                continue
            
            # Flip image for mirror effect
            img = cv2.flip(img, 1)
            
            # Detect hands
            img = self.detector.find_hands(img, draw=True)
            
            # Calculate cuboid parameters from hand positions
            cuboid_data = self._calculate_cuboid_parameters()
            
            # Update frame and data
            with self.lock:
                self.frame = img
                self.latest_data = cuboid_data
            
            # Update outputs
            if cuboid_data:
                self.cuboid_height = cuboid_data['height']
                self.cuboid_width = cuboid_data['width'] 
                self.cuboid_depth = cuboid_data['depth']
                self.cuboid_rotation_x = cuboid_data['rotation_x']
                self.cuboid_rotation_y = cuboid_data['rotation_y']
                self.cuboid_rotation_z = cuboid_data['rotation_z']
    
    def _calculate_cuboid_parameters(self):
        """Calculate cuboid dimensions from hand positions"""
        if self.detector.hand_count < 2:
            return None
        
        hand1 = self.detector.key_landmarks_list[0]
        hand2 = self.detector.key_landmarks_list[1]
        
        # Calculate basic dimensions from hand distances
        wrist_dist = self._calculate_distance(hand1['wrist'], hand2['wrist'])
        thumb_dist = self._calculate_distance(hand1['thumb'], hand2['thumb'])
        index_dist = self._calculate_distance(hand1['index'], hand2['index'])
        
        # Width based on hand spread within each hand
        hand1_width = self._calculate_distance(hand1['thumb'], hand1['pinky'])
        hand2_width = self._calculate_distance(hand2['thumb'], hand2['pinky'])
        
        # Height based on vertical distance from wrist to fingers
        hand1_height = self._calculate_vertical_span(hand1)
        hand2_height = self._calculate_vertical_span(hand2)
        
        # Normalize values (you may need to adjust these scaling factors)
        width = (hand1_width + hand2_width) / 2 / 300.0  # Normalize
        height = (hand1_height + hand2_height) / 2 / 300.0  # Normalize  
        depth = (wrist_dist + thumb_dist + index_dist) / 3 / 400.0  # Normalize
        
        # Calculate rotations based on hand orientation
        rotation_x, rotation_y, rotation_z = self._calculate_rotations(hand1, hand2)
        
        return {
            'width': max(0.1, min(2.0, width)),
            'height': max(0.1, min(2.0, height)),
            'depth': max(0.1, min(2.0, depth)),
            'rotation_x': rotation_x,
            'rotation_y': rotation_y, 
            'rotation_z': rotation_z
        }
    
    def _calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def _calculate_vertical_span(self, hand):
        """Calculate vertical span of hand from wrist to highest finger"""
        wrist_y = hand['wrist'][1]
        min_y = min(hand['thumb'][1], hand['index'][1], hand['pinky'][1])
        return abs(wrist_y - min_y)
    
    def _calculate_rotations(self, hand1, hand2):
        """Calculate rotations based on hand positions and orientations"""
        # Rotation X: based on vertical difference between hands
        rotation_x = (hand2['wrist'][1] - hand1['wrist'][1]) / 200.0
        
        # Rotation Y: based on horizontal spread between hands  
        rotation_y = (hand2['wrist'][0] - hand1['wrist'][0]) / 300.0
        
        # Rotation Z: based on hand tilt (simplified)
        hand1_tilt = self._calculate_hand_tilt(hand1)
        hand2_tilt = self._calculate_hand_tilt(hand2)
        rotation_z = (hand1_tilt + hand2_tilt) / 2.0
        
        return rotation_x, rotation_y, rotation_z
    
    def _calculate_hand_tilt(self, hand):
        """Calculate approximate hand tilt"""
        # Simple tilt calculation based on wrist to middle finger vector
        wrist = hand['wrist']
        middle = [(hand['index'][0] + hand['ring'][0]) / 2,
                 (hand['index'][1] + hand['ring'][1]) / 2]
        
        dx = middle[0] - wrist[0]
        dy = middle[1] - wrist[1]
        
        return np.arctan2(dy, dx) / np.pi  # Normalize to -1 to 1
    
    def step(self):
        """Update step - called by the audio engine"""
        self.getInputs()
        
        # Update visual display periodically for performance
        if self.time % 30 == 0:  # Update every 30 steps
            self._update_visual_display()
        
        self.time += 1
    
    def _update_visual_display(self):
        """Update the visual display with current frame and data"""
        if not hasattr(self, 'video_label') or not self.video_label:
            return
            
        with self.lock:
            frame = self.frame
            data = self.latest_data
        
        if frame is not None:
            # Convert frame to QImage
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale while maintaining aspect ratio
            pixmap = pixmap.scaled(320, 240, Qt.KeepAspectRatio)
            self.video_label.setPixmap(pixmap)
        
        # Update data display
        if data:
            data_text = (f"W: {data['width']:.2f} | "
                        f"H: {data['height']:.2f} | "
                        f"D: {data['depth']:.2f}\n"
                        f"RX: {data['rotation_x']:.2f} | "
                        f"RY: {data['rotation_y']:.2f} | "
                        f"RZ: {data['rotation_z']:.2f}")
        else:
            data_text = "Waiting for two hands..."
            
        self.data_label.setText(data_text)
    
    def stop(self):
        """Clean up resources"""
        self.running = False
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.stop()