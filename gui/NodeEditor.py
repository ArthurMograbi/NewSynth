# gui/NodeEditor.py
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QKeyEvent
from .Node import Node
from .Connection import Connection
from .Port import Port

class NodeEditorView(QGraphicsView):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHints(self.renderHints())
        
        self._drag_start = None
        self._connection_in_progress = None
        
        # Map of patch instances to node objects
        self.node_map = {}
        
        # Add existing patches to the scene
        for patch in board.patches:
            self.add_node_for_patch(patch)
            
    def add_node_for_patch(self, patch):
        node = Node(patch)
        self.scene.addItem(node)
        self.node_map[patch] = node
        return node
        
    def contextMenuEvent(self, event):
        context_menu = QMenu()
        
        # Add actions for each patch type
        patch_types = self._discover_patch_types()
        for patch_name, patch_class in patch_types.items():
            action = QAction(f"Add {patch_name}", self)
            action.triggered.connect(lambda checked, cls=patch_class: self.add_patch(cls))
            context_menu.addAction(action)
            
        context_menu.exec_(event.globalPos())
        
    def _discover_patch_types(self):
        # This would import and discover all available patch classes
        # For simplicity, we'll return a hardcoded list
        from patches import SineGenerator, AudioOutput, MouseData, WavePlayer
        return {
            "Sine Generator": SineGenerator,
            "Audio Output": AudioOutput,
            "Mouse Data": MouseData,
            "Wave Player": WavePlayer
        }
        
    def add_patch(self, patch_class):
        # Instantiate the patch
        patch = patch_class()
        
        # Add to board
        self.board.add_patch(patch)
        
        # Create and add node to scene
        node = self.add_node_for_patch(patch)
        node.setPos(self.mapToScene(QPoint(100, 100)))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.itemAt(event.pos())
            if isinstance(item, Port):
                self._drag_start = item
                self._connection_in_progress = Connection(item, None)
                self.scene.addItem(self._connection_in_progress)
                return
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self._connection_in_progress:
            # Update the end position of the connection
            mouse_pos = self.mapToScene(event.pos())
            self._connection_in_progress.end_port_pos = mouse_pos
            self._connection_in_progress._update_path()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if self._connection_in_progress and event.button() == Qt.LeftButton:
            # Check if we're releasing over a port
            item = self.itemAt(event.pos())
            if isinstance(item, Port) and item != self._drag_start:
                # Check if connection is valid
                if (self._drag_start.is_output != item.is_output and
                    self._drag_start.node != item.node):
                    
                    # Create the actual connection
                    final_connection = Connection(self._drag_start, item)
                    self.scene.addItem(final_connection)
                    
                    # Make the patch connection
                    if self._drag_start.is_output:
                        output_patch = self._drag_start.node.patch
                        output_prop = self._drag_start.name
                        input_patch = item.node.patch
                        input_prop = item.name
                    else:
                        output_patch = item.node.patch
                        output_prop = item.name
                        input_patch = self._drag_start.node.patch
                        input_prop = self._drag_start.name
                        
                    from patches.Patch import Patch
                    Patch.connect(input_patch, output_patch, input_prop, output_prop)
            
            # Clean up temporary connection
            self.scene.removeItem(self._connection_in_progress)
            self._connection_in_progress = None
            self._drag_start = None
            
        super().mouseReleaseEvent(event)