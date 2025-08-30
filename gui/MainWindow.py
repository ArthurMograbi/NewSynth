# gui/MainWindow.py
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QToolBar, QAction, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt
from .NodeEditor import NodeEditorView
from .Node import Node

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
        
        # Create info panel
        info_dock = QDockWidget("Patch Info", self)
        info_widget = QWidget()
        info_layout = QVBoxLayout()
        
        self.info_label = QLabel("Select a patch to view details")
        info_layout.addWidget(self.info_label)
        
        info_widget.setLayout(info_layout)
        info_dock.setWidget(info_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, info_dock)
        
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
        
        # Set central widget
        self.setCentralWidget(self.editor)
        
        # Connect selection change event
        self.editor.scene.selectionChanged.connect(self.on_selection_changed)
        
        # Show the window
        self.show()
        
    def on_selection_changed(self):
        selected_items = self.editor.scene.selectedItems()
        if selected_items and isinstance(selected_items[0], Node):
            node = selected_items[0]
            patch = node.patch
            
            # Generate info text
            info_text = f"<h2>{node.title}</h2>"
            info_text += f"<p>Type: {patch.__class__.__name__}</p>"
            
            # Show inputs and outputs
            metadata = getattr(patch, '_metadata', {})
            io_data = metadata.get('io', {})
            
            if io_data:
                info_text += "<h3>Inputs:</h3><ul>"
                for input_name in [k for k, v in io_data.items() if v == "in"]:
                    info_text += f"<li>{input_name}</li>"
                info_text += "</ul>"
                
                info_text += "<h3>Outputs:</h3><ul>"
                for output_name in [k for k, v in io_data.items() if v == "out"]:
                    info_text += f"<li>{output_name}</li>"
                info_text += "</ul>"
            
            self.info_label.setText(info_text)
        else:
            self.info_label.setText("Select a patch to view details")