# gui/Node.py
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPen, QBrush, QColor, QPainterPath
from .Port import Port

class Node(QGraphicsItem):
    def __init__(self, patch, title=None):
        super().__init__()
        self.patch = patch
        self.title = title or patch.__class__.__name__
        self.width = 200
        self.height = 100
        self.edge_radius = 5.0
        self.title_height = 24
        self.port_spacing = 20
        self._inputs = []
        self._outputs = []
        self._text_items = []
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)  # Flag for item moved event
        self._init_ui()
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            # Update all connections when node moves
            for port in self._inputs + self._outputs:
                for connection in port._connections:
                    connection.update_path_from_ports()
        return super().itemChange(change, value)
        
    def _init_ui(self):
        # Create title
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self.title)
        self.title_item.setDefaultTextColor(Qt.white)
        
        # Position title
        title_rect = self.title_item.boundingRect()
        self.title_item.setPos(
            (self.width - title_rect.width()) / 2,
            5
        )
        
        # Create ports based on metadata
        metadata = getattr(self.patch, '_metadata', {})
        io_data = metadata.get('io', {})
        waveio_data = metadata.get('waveio', {})
        
        # Input ports
        y_offset = self.title_height + 10
        for input_name in [k for k, v in io_data.items() if v == "in"]:
            # Create port
            port = Port(self, input_name, is_output=False)
            port.setPos(5, y_offset)
            self._inputs.append(port)
            
            # Create text label for port
            text_item = QGraphicsTextItem(input_name, self)
            text_item.setDefaultTextColor(Qt.white)
            text_item.setPos(20, y_offset - 5)
            self._text_items.append(text_item)
            
            y_offset += self.port_spacing
            
        # Waveform input ports
        for input_name in [k for k, v in waveio_data.items() if v == "in"]:
            # Create waveform port with yellow border
            port = Port(self, input_name, is_output=False, is_waveform=True)
            port.setPos(5, y_offset)
            self._inputs.append(port)
            
            # Create text label for port
            text_item = QGraphicsTextItem(input_name, self)
            text_item.setDefaultTextColor(Qt.white)
            text_item.setPos(20, y_offset - 5)
            self._text_items.append(text_item)
            
            y_offset += self.port_spacing
        
        # Output ports
        y_offset = self.title_height + 10
        for output_name in [k for k, v in io_data.items() if v == "out"]:
            # Create port
            port = Port(self, output_name, is_output=True)
            port.setPos(self.width - 15, y_offset)
            self._outputs.append(port)
            
            # Create text label for port
            text_item = QGraphicsTextItem(output_name, self)
            text_item.setDefaultTextColor(Qt.white)
            text_rect = text_item.boundingRect()
            text_item.setPos(self.width - 20 - text_rect.width(), y_offset - 5)
            self._text_items.append(text_item)
            
            y_offset += self.port_spacing
            
        # Set minimum height based on ports
        self.height = max(self.height, y_offset + 10)
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget):
        # Draw node background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width, self.height, self.edge_radius, self.edge_radius)
        
        painter.setPen(QPen(Qt.darkGray if not self.isSelected() else Qt.blue, 1.5))
        painter.setBrush(QBrush(QColor(60, 60, 60, 200)))
        painter.drawPath(path)
        
        # Draw title background
        title_path = QPainterPath()
        title_path.addRoundedRect(0, 0, self.width, self.title_height, 
                                 self.edge_radius, self.edge_radius)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(30, 30, 30)))
        painter.drawPath(title_path)

# Add a new class for Waveform nodes
class WaveformNode(Node):
    def __init__(self, waveform, title=None):
        super().__init__(waveform, title or waveform.__class__.__name__)
        self.waveform = waveform
        
    def _init_ui(self):
        # Initialize port lists
        self._inputs = []
        self._outputs = []
        
        self.title_item = QGraphicsTextItem(self)
        self.title_item.setPlainText(self.title)
        self.title_item.setDefaultTextColor(Qt.white)
        
        # Position title
        title_rect = self.title_item.boundingRect()
        self.title_item.setPos(
            (self.width - title_rect.width()) / 2,
            5
        )
        
        # Create output port for waveform
        y_offset = self.title_height + 10
        port = Port(self, "wave", is_output=True, is_waveform=True)
        port.setPos(self.width - 15, y_offset)
        self._outputs.append(port)
        
        # Create text label for port
        text_item = QGraphicsTextItem("wave", self)
        text_item.setDefaultTextColor(Qt.white)
        text_rect = text_item.boundingRect()
        text_item.setPos(self.width - 20 - text_rect.width(), y_offset - 5)
        self._text_items.append(text_item)
        
        # Set minimum height based on ports
        self.height = max(self.height, y_offset + 20)
        
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)