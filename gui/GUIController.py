# gui/GUIController.py
from PyQt5.QtCore import QObject, pyqtSignal
from .NodeEditor import NodeEditorView
from .MainWindow import MainWindow
from Board import Board

class GUIController(QObject):
    """Main controller that coordinates between the Board model and GUI views"""
    
    # Signals for board state changes
    board_loaded = pyqtSignal()
    board_saved = pyqtSignal(str)
    patch_added = pyqtSignal(object)
    patch_removed = pyqtSignal(object)
    
    def __init__(self, board=None):
        super().__init__()
        self.board = board or Board()
        self.main_window = None
        self.node_editor = None
        
    def initialize_ui(self):
        """Initialize the complete GUI interface"""
        self.node_editor = NodeEditorView(self.board)
        self.main_window = MainWindow(self.board)
        self.main_window.set_editor(self.node_editor)
        
        # Connect signals
        self._connect_signals()
        
        return self.main_window
    
    def _connect_signals(self):
        """Connect all controller signals"""
        # Connect node editor events to controller methods
        self.node_editor.patch_added.connect(self._on_patch_added)
        self.node_editor.patch_removed.connect(self._on_patch_removed)
        self.node_editor.connection_made.connect(self._on_connection_made)
        
        # Connect main window events
        self.main_window.save_requested.connect(self.save_board)
        self.main_window.load_requested.connect(self.load_board)
    
    def _on_patch_added(self, patch):
        """Handle new patch added via GUI"""
        self.board.add_patch(patch)
        self.patch_added.emit(patch)
    
    def _on_patch_removed(self, patch):
        """Handle patch removed via GUI"""
        self.board.remove_patch(patch)
        self.patch_removed.emit(patch)
    
    def _on_connection_made(self, from_patch, from_port, to_patch, to_port):
        """Handle new connection made in GUI"""
        from patches.Patch import Patch
        Patch.connect(to_patch, from_patch, to_port, from_port)
    
    def save_board(self, filename):
        """Save current board state"""
        patch_positions = {}
        waveform_positions = {}
        
        # Collect positions from node editor
        if self.node_editor:
            for patch, node in self.node_editor.node_map.items():
                patch_positions[patch] = (node.x(), node.y())
            for waveform, node in self.node_editor.waveform_map.items():
                waveform_positions[waveform] = (node.x(), node.y())
        
        self.board.save_to_file(filename, patch_positions, waveform_positions)
        self.board_saved.emit(filename)
    
    # In gui/GUIController.py, update the load_board method:
    def load_board(self, filename):
        """Load board from file"""
        board, patch_positions, waveform_positions = Board.load_from_file(filename)
        
        # Update controller state
        self.board = board
        
        # CRITICAL: Update the main window's board reference
        if self.main_window:
            self.main_window.board = board
        
        # Update UI
        if self.node_editor:
            self.node_editor.load_board_state(board, patch_positions, waveform_positions)
        
        self.board_loaded.emit()