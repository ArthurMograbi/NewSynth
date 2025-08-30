# gui/Port.py
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt

class Port(QGraphicsItem):
    def __init__(self, node, name, is_output=False, is_waveform=False):
        super().__init__(node)
        self.node = node
        self.name = name
        self.is_output = is_output
        self.is_waveform = is_waveform
        self.radius = 6  # Slightly larger radius
        self.margin = 2
        self._connections = []
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 
                     2 * self.radius, 2 * self.radius)
        
    def paint(self, painter, option, widget):
        # Set pen width based on port type
        pen_width = 3 if self.is_waveform else 2  # Thicker border for waveform ports
        
        # Set pen color based on port type
        if self.is_waveform:
            pen_color = QColor(255, 255, 0)  # Yellow for waveform ports
        else:
            pen_color = Qt.darkGray
            
        painter.setPen(QPen(pen_color, pen_width))
        
        # Set brush color
        brush_color = Qt.darkGreen if self.is_output else Qt.darkRed
        painter.setBrush(QBrush(brush_color))
        
        painter.drawEllipse(-self.radius, -self.radius, 
                          2 * self.radius, 2 * self.radius)
        
    def get_socket_position(self):
        """Get the scene position of the socket"""
        return self.mapToScene(QPointF(0, 0))