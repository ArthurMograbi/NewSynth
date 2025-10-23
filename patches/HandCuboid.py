# patches/HandCuboid.py
import cv2
import mediapipe as mp
import numpy as np
import threading
from .VisualPatch import VisualPatch
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

class CuboidDrawer:
    def __init__(self, 
                 max_thickness=10, 
                 min_thickness=1, 
                 max_distance=700,
                 color=(0, 255, 0)):
        
        self.config = {
            'max_thickness': max_thickness,
            'min_thickness': min_thickness,
            'max_distance': max_distance,
            'color': color
        }
        
        self.vertices = []
        self.edges = []
        self.line_thickness = 0
        self.avg_distance = 0
        
    def calculate_average_distance(self, hand1_landmarks, hand2_landmarks):
        """Calculate the average distance between corresponding landmarks of two hands"""
        total_distance = 0
        count = 0
        
        for key in ['pinky', 'ring', 'index', 'thumb']:
            point1 = np.array(hand1_landmarks[key])
            point2 = np.array(hand2_landmarks[key])
            distance = np.linalg.norm(point1 - point2)
            total_distance += distance
            count += 1
        
        self.avg_distance = total_distance / count if count > 0 else 0
        return self.avg_distance
    
    def _calculate_line_thickness(self, avg_distance):
        """Calculate dynamic line thickness based on distance"""
        max_t = self.config['max_thickness']
        min_t = self.config['min_thickness']
        max_d = self.config['max_distance']
        
        thickness = max_t - (avg_distance / max_d) * (max_t - min_t)
        return max(min_t, min(max_t, int(thickness)))
    
    def _define_cuboid_vertices(self, hand1_landmarks, hand2_landmarks):
        """Define cuboid vertices from hand landmarks"""
        vertices = [
            hand1_landmarks['pinky'],   # Vertex 0: left hand pinky
            hand1_landmarks['ring'],    # Vertex 1: left hand ring
            hand1_landmarks['index'],   # Vertex 2: left hand index
            hand1_landmarks['thumb'],   # Vertex 3: left hand thumb
            
            hand2_landmarks['pinky'],   # Vertex 4: right hand pinky
            hand2_landmarks['ring'],    # Vertex 5: right hand ring
            hand2_landmarks['index'],   # Vertex 6: right hand index
            hand2_landmarks['thumb']    # Vertex 7: right hand thumb
        ]
        
        self.vertices = [np.array(v, dtype=np.int32) for v in vertices]
        return self.vertices
    
    def _define_cuboid_edges(self):
        """Define the edges of the cuboid"""
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # Front face (left hand)
            (4, 5), (5, 6), (6, 7), (7, 4),  # Back face (right hand)
            (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
        ]
        return self.edges
    
    def draw_cuboid(self, img, hand1_landmarks, hand2_landmarks):
        """Draw an irregular cuboid between two sets of hand landmarks"""
        if not hand1_landmarks or not hand2_landmarks:
            return img
            
        # Calculate average distance and line thickness
        self.calculate_average_distance(hand1_landmarks, hand2_landmarks)
        self.line_thickness = self._calculate_line_thickness(self.avg_distance)
        
        # Define vertices and edges
        self._define_cuboid_vertices(hand1_landmarks, hand2_landmarks)
        self._define_cuboid_edges()
        
        # Draw the edges with dynamic thickness
        for edge in self.edges:
            start_idx, end_idx = edge
            start_point = tuple(self.vertices[start_idx])
            end_point = tuple(self.vertices[end_idx])
            cv2.line(img, start_point, end_point, self.config['color'], self.line_thickness)
        
        # Draw vertices as circles
        vertex_size = max(3, 6 - self.line_thickness // 2)
        for i, vertex in enumerate(self.vertices):
            cv2.circle(img, tuple(vertex), vertex_size, self.config['color'], -1)
            cv2.circle(img, tuple(vertex), vertex_size + 2, (255, 255, 255), 1)
            
        return img

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
        self.cuboid_drawer = CuboidDrawer()
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.frame = None
        self.latest_data = None
        self.lock = threading.Lock()
        
        # Create visual element with proper sizing
        self.visual_element = self._create_visual_element()
        
        # Start hand tracking thread
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
        # Use QTimer for UI updates instead of step() method
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_visual_display)
        self.update_timer.start(33)  # ~30 FPS
    
    def _create_visual_element(self):
        """Create the visual display for hand tracking with proper sizing"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)  # Reduce margins
        layout.setSpacing(2)  # Reduce spacing
        
        # Video label with fixed size policy
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(200, 150)  # Reduced minimum size
        self.video_label.setMaximumSize(300, 225)  # Set maximum size
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_label.setStyleSheet("border: 1px solid gray; background-color: black;")
        self.video_label.setText("Initializing camera...")
        
        # Data label with fixed height
        self.data_label = QLabel()
        self.data_label.setAlignment(Qt.AlignCenter)
        self.data_label.setMaximumHeight(40)  # Fixed height for data
        self.data_label.setStyleSheet("background-color: #2d2d2d; color: white; padding: 2px;")
        self.data_label.setText("Waiting for two hands...")
        
        layout.addWidget(self.video_label)
        layout.addWidget(self.data_label)
        
        # Set widget size policy
        widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        widget.setMaximumSize(320, 280)  # Constrain overall size
        
        return widget
    
    def _tracking_loop(self):
        """Main hand tracking loop running in separate thread"""
        while self.running:
            success, img = self.cap.read()
            if not success:
                continue
            
            # Flip image for mirror effect
            img = cv2.flip(img, 1)
            
            # Detect hands and draw landmarks
            img = self.detector.find_hands(img, draw=True)
            
            # Draw cuboid if two hands are detected
            if self.detector.hand_count >= 2:
                hand1_landmarks = self.detector.key_landmarks_list[0]
                hand2_landmarks = self.detector.key_landmarks_list[1]
                img = self.cuboid_drawer.draw_cuboid(img, hand1_landmarks, hand2_landmarks)
                
                # Calculate cuboid parameters
                cuboid_data = self._calculate_cuboid_parameters()
                
                # Update outputs
                if cuboid_data:
                    self.cuboid_height = cuboid_data['height']
                    self.cuboid_width = cuboid_data['width'] 
                    self.cuboid_depth = cuboid_data['depth']
                    self.cuboid_rotation_x = cuboid_data['rotation_x']
                    self.cuboid_rotation_y = cuboid_data['rotation_y']
                    self.cuboid_rotation_z = cuboid_data['rotation_z']
                    
                    with self.lock:
                        self.latest_data = cuboid_data
            else:
                with self.lock:
                    self.latest_data = None
            
            # Update frame
            with self.lock:
                self.frame = img
    
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
        
        # Normalize values
        width = (hand1_width + hand2_width) / 2 / 300.0
        height = (hand1_height + hand2_height) / 2 / 300.0  
        depth = (wrist_dist + thumb_dist + index_dist) / 3 / 400.0
        
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
        wrist = hand['wrist']
        middle = [(hand['index'][0] + hand['ring'][0]) / 2,
                 (hand['index'][1] + hand['ring'][1]) / 2]
        
        dx = middle[0] - wrist[0]
        dy = middle[1] - wrist[1]
        
        return np.arctan2(dy, dx) / np.pi
    
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
            
            # Scale to fit the label while maintaining aspect ratio
            self.video_label.setPixmap(pixmap.scaled(
                self.video_label.width(), 
                self.video_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        
        # Update data display
        if data:
            data_text = (f"W: {data['width']:.2f} H: {data['height']:.2f} D: {data['depth']:.2f}\n"
                        f"RX: {data['rotation_x']:.2f} RY: {data['rotation_y']:.2f} RZ: {data['rotation_z']:.2f}")
        else:
            data_text = "Show two hands to control cuboid"
            
        self.data_label.setText(data_text)
    
    def step(self):
        """Update step - called by the audio engine"""
        self.getInputs()
        self.time += 1
    
    def stop(self):
        """Clean up resources"""
        self.running = False
        if hasattr(self, 'update_timer') and self.update_timer.isActive():
            self.update_timer.stop()
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.stop()