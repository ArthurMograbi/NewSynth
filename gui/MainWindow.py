# gui/MainWindow.py
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QToolBar, QAction
from PyQt5.QtCore import Qt
from .NodeEditor import NodeEditorView

class MainWindow(QMainWindow):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Modular Synth")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create node editor
        self.editor = NodeEditorView(self.board)
        self.setCentralWidget(self.editor)
        
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Play/Stop actions
        play_action = QAction("Play", self)
        play_action.triggered.connect(self.board.play)
        toolbar.addAction(play_action)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.board.stop)
        toolbar.addAction(stop_action)
        
        # Show the window
        self.show()