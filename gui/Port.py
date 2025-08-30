# gui/Port.py
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor
from PyQt5.QtCore import Qt

class Port(QGraphicsItem):
    def __init__(self, node, name, is_output=False):
        super().__init__(node)
        self.node = node
        self.name = name
        self.is_output = is_output
        self.radius = 5
        self.margin = 2
        self._connections = []
        
    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 
                     2 * self.radius, 2 * self.radius)
        
    def paint(self, painter, option, widget):
        # Draw port circle
        painter.setPen(QPen(Qt.darkGray))
        painter.setBrush(QBrush(Qt.darkGreen if self.is_output else Qt.darkRed))
        painter.drawEllipse(-self.radius, -self.radius, 
                          2 * self.radius, 2 * self.radius)
        
    def get_socket_position(self):
        """Get the scene position of the socket"""
        return self.mapToScene(QPointF(0, 0))