# gui/NodeEditor.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QAction, QFileDialog
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QWheelEvent
import importlib
import inspect
from .Node import Node, WaveformNode
from .Connection import Connection
from .Port import Port
from patches.waveforms import FileWave, FunctionWave
import math

class NodeEditorView(QGraphicsView):
    # Define signals for editor events
    patch_added = pyqtSignal(object)  # Emitted when a patch is added via GUI
    patch_removed = pyqtSignal(object)  # Emitted when a patch is removed via GUI
    connection_made = pyqtSignal(object, str, object, str)  # from_patch, from_port, to_patch, to_port
    
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints())
        
        self._drag_start = None
        self._temp_connection = None
        
        # Map of patch instances to node objects
        self.node_map = {}
        # Map of waveform instances to node objects
        self.waveform_map = {}
        
        # Zoom settings
        self.zoom_factor = 1.15
        self.zoom = 10
        self.zoom_min = 0
        self.zoom_max = 20
        
        # Add existing patches to the scene
        for patch in board.patches:
            self.add_node_for_patch(patch)
            
    def wheelEvent(self, event: QWheelEvent):
        # Zoom in/out with mouse wheel
        if event.modifiers() & Qt.ControlModifier:
            zoom_in = event.angleDelta().y() > 0
            
            if zoom_in and self.zoom < self.zoom_max:
                self.zoom += 1
                self.scale(self.zoom_factor, self.zoom_factor)
            elif not zoom_in and self.zoom > self.zoom_min:
                self.zoom -= 1
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        else:
            # Default scrolling behavior when Ctrl is not pressed
            super().wheelEvent(event)
            
    def add_node_for_patch(self, patch):
        """Add a visual node for a patch"""
        node = Node(patch)
        self.scene.addItem(node)
        self.node_map[patch] = node
        return node
        
    def add_waveform_node(self, waveform):
        """Add a waveform node to the scene"""
        node = WaveformNode(waveform)
        self.scene.addItem(node)
        self.waveform_map[waveform] = node
        return node
        
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        
        # Create "Add Patch" submenu
        patch_menu = context_menu.addMenu("Add Patch")
        patch_types = self._discover_patch_types()
        for patch_name, patch_class in patch_types.items():
            action = QAction(f"{patch_name}", self)
            action.triggered.connect(lambda checked, cls=patch_class: self._create_patch(cls, event.pos()))
            patch_menu.addAction(action)
        
        # Create "Add Waveform" submenu
        waveform_menu = context_menu.addMenu("Add Waveform")
        file_wave_action = QAction("FileWave", self)
        file_wave_action.triggered.connect(lambda: self._create_file_wave(event.pos()))
        waveform_menu.addAction(file_wave_action)
        
        func_wave_action = QAction("FunctionWave", self)
        func_wave_action.triggered.connect(lambda: self._create_function_wave(event.pos()))
        waveform_menu.addAction(func_wave_action)
        
        context_menu.exec_(event.globalPos())
        
    def _discover_patch_types(self):
        """Discover all available patch classes automatically"""
        patch_types = {}
        
        try:
            patches_module = importlib.import_module('patches')
            
            for name, obj in inspect.getmembers(patches_module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '_metadata') and 
                    issubclass(obj, patches_module.Patch) and 
                    obj != patches_module.Patch):
                    patch_types[name] = obj
                    
        except ImportError as e:
            print(f"Error discovering patch types: {e}")
            
        return patch_types
    
    def _create_patch(self, patch_class, pos):
        """Create a new patch and add it to the scene"""
        patch = patch_class()
        node = self.add_node_for_patch(patch)
        node.setPos(self.mapToScene(pos))
        self.patch_added.emit(patch)
        
    def _create_file_wave(self, pos):
        """Create a FileWave from a selected file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", "Audio Files (*.wav *.mp3 *.ogg *.flac)"
        )
        
        if filename:
            try:
                file_wave = FileWave(filename)
                node = self.add_waveform_node(file_wave)
                node.setPos(self.mapToScene(pos))
            except Exception as e:
                print(f"Error loading audio file: {e}")
        
    def _create_function_wave(self, pos):
        """Create a FunctionWave with a default function"""
        func = lambda x: math.sin(x * 2 * math.pi)
        func_wave = FunctionWave(func)
        node = self.add_waveform_node(func_wave)
        node.setPos(self.mapToScene(pos))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, Port):
                self._drag_start = item
                self._temp_connection = Connection(item, None)
                self.scene.addItem(self._temp_connection)
                return
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self._temp_connection:
            mouse_pos = self.mapToScene(event.pos())
            item = self.itemAt(event.pos())
            
            if isinstance(item, Port):
                self._temp_connection.set_end_port(item)
            else:
                temp_port = type('TempPort', (), {
                    'get_socket_position': lambda x: mouse_pos,
                    '_connections':[]
                })()
                self._temp_connection.set_end_port(temp_port)
                
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self._temp_connection and event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            
            if isinstance(item, Port) and item != self._drag_start:
                if (self._drag_start.is_output != item.is_output and
                    self._drag_start.node != item.node):
                    
                    if self._drag_start.is_waveform and item.is_waveform:
                        # Handle waveform connection
                        if self._drag_start.is_output:
                            waveform = self._drag_start.node.waveform
                            setattr(item.node.patch, item.name, waveform)
                            final_connection = Connection(self._drag_start, item)
                            self.scene.addItem(final_connection)
                    else:
                        # Handle regular patch connection
                        final_connection = Connection(self._drag_start, item)
                        self.scene.addItem(final_connection)
                        
                        # Emit connection signal
                        if self._drag_start.is_output:
                            self.connection_made.emit(
                                self._drag_start.node.patch, self._drag_start.name,
                                item.node.patch, item.name
                            )
                        else:
                            self.connection_made.emit(
                                item.node.patch, item.name,
                                self._drag_start.node.patch, self._drag_start.name
                            )
            
            # Clean up temporary connection
            self.scene.removeItem(self._temp_connection)
            self._temp_connection = None
            self._drag_start = None
            
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
        else:
            super().keyPressEvent(event)
            
    def delete_selected(self):
        """Delete selected nodes and their connections"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, Node):
                # Remove all connections first
                for port in item._inputs + item._outputs:
                    for connection in port._connections[:]:
                        connection.disconnect()
                
                # Remove from maps and emit signal if it's a patch
                if hasattr(item, 'patch'):
                    if item.patch in self.node_map:
                        del self.node_map[item.patch]
                    self.patch_removed.emit(item.patch)
                elif hasattr(item, 'waveform') and item.waveform in self.waveform_map:
                    del self.waveform_map[item.waveform]
                
                self.scene.removeItem(item)
    
    def load_board_state(self, board, patch_positions, waveform_positions):
        """Load a complete board state into the editor"""
        self.scene.clear()
        self.node_map.clear()
        self.waveform_map.clear()
        
        self.board = board
        
        # Add patches to editor
        for patch in board.patches:
            node = self.add_node_for_patch(patch)
            if patch in patch_positions:
                pos = patch_positions[patch]
                node.setPos(*pos)
        
        # Note: Waveform loading would need additional implementation
        # based on how waveforms are stored in your patches
        
        # Recreate connections visually
        self.recreate_connections()
    
    def recreate_connections(self):
        """Recreate visual connections based on patch connections"""
        # This would need to iterate through all patches and their connections
        # to recreate the visual representation
        # Implementation depends on your specific connection storage
        pass