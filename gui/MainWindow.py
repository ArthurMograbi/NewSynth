# gui/MainWindow.py
from PyQt5.QtWidgets import (QMainWindow, QDockWidget, QToolBar, QAction, 
                             QVBoxLayout, QWidget, QLabel, QLineEdit, QFormLayout,
                             QScrollArea, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from .NodeEditor import NodeEditorView
from .Node import Node

class MainWindow(QMainWindow):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.current_node = None
        self.input_widgets = {}  # Store input widgets for easy access
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
        
        # Create a scroll area for the info panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.info_layout = QFormLayout(scroll_content)
        
        scroll_area.setWidget(scroll_content)
        info_layout.addWidget(scroll_area)
        
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

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.editor.delete_selected)
        toolbar.addAction(delete_action)
        
        # Set central widget
        self.setCentralWidget(self.editor)
        
        # Connect selection change event
        self.editor.scene.selectionChanged.connect(self.on_selection_changed)
        
        # Show the window
        self.show()
        
    def on_selection_changed(self):
        # Clear previous input widgets
        self.clear_input_widgets()
        
        selected_items = self.editor.scene.selectedItems()
        if selected_items and isinstance(selected_items[0], Node):
            node = selected_items[0]
            self.current_node = node
            patch = node.patch
            
            # Generate info text
            info_text = f"<h2>{node.title}</h2>"
            info_text += f"<p>Type: {patch.__class__.__name__}</p>"
            
            # Create a label for the basic info
            info_label = QLabel(info_text)
            self.info_layout.addRow(info_label)
            
            # Show inputs and outputs
            metadata = getattr(patch, '_metadata', {})
            io_data = metadata.get('io', {})
            
            if io_data:
                # Add inputs section header
                inputs_label = QLabel("<h3>Inputs:</h3>")
                self.info_layout.addRow(inputs_label)
                
                # Add input fields for unconnected inputs
                for input_name in [k for k, v in io_data.items() if v == "in"]:
                    # Find the port for this input
                    port = None
                    for p in node._inputs:
                        if p.name == input_name:
                            port = p
                            break
                    
                    # Check if the port is connected
                    is_connected = port and port._connections
                    
                    # Create a label for the input
                    input_label = QLabel(input_name)
                    
                    # Create an input widget based on the expected type
                    if hasattr(patch, input_name):
                        current_value = getattr(patch, input_name)
                        
                        if isinstance(current_value, (int, float)):
                            # Use a spin box for numeric values
                            spin_box = QDoubleSpinBox()
                            spin_box.setRange(-1000, 1000)
                            spin_box.setDecimals(4)
                            spin_box.setSingleStep(0.1)
                            spin_box.setValue(float(current_value))
                            spin_box.setEnabled(not is_connected)
                            
                            # Connect the value change signal
                            spin_box.valueChanged.connect(
                                lambda value, name=input_name: self.update_input_value(name, value)
                            )
                            
                            self.info_layout.addRow(input_label, spin_box)
                            self.input_widgets[input_name] = spin_box
                        else:
                            # Use a line edit for other types
                            line_edit = QLineEdit(str(current_value))
                            line_edit.setEnabled(not is_connected)
                            
                            # Connect the editing finished signal
                            line_edit.editingFinished.connect(
                                lambda name=input_name, edit=line_edit: self.update_input_value(name, edit.text())
                            )
                            
                            self.info_layout.addRow(input_label, line_edit)
                            self.input_widgets[input_name] = line_edit
                
                # Add outputs section header
                outputs_label = QLabel("<h3>Outputs:</h3>")
                self.info_layout.addRow(outputs_label)
                
                # List output ports
                for output_name in [k for k, v in io_data.items() if v == "out"]:
                    output_label = QLabel(output_name)
                    self.info_layout.addRow(output_label)
        else:
            # Add a placeholder label when nothing is selected
            placeholder = QLabel("Select a patch to view details")
            self.info_layout.addRow(placeholder)
            self.current_node = None
    
    def clear_input_widgets(self):
        """Clear all input widgets from the info layout"""
        # Remove all rows from the layout
        while self.info_layout.count():
            item = self.info_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.input_widgets.clear()
    
    def update_input_value(self, input_name, value):
        """Update the value of an input on the current patch"""
        if self.current_node and hasattr(self.current_node.patch, input_name):
            # Convert value to the appropriate type
            current_value = getattr(self.current_node.patch, input_name)
            
            if isinstance(current_value, float):
                setattr(self.current_node.patch, input_name, float(value))
            elif isinstance(current_value, int):
                setattr(self.current_node.patch, input_name, int(float(value)))
            else:
                setattr(self.current_node.patch, input_name, value)