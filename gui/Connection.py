# gui/Connection.py
from PyQt5.QtWidgets import QGraphicsPathItem
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QPainterPath, QPen, QColor

class Connection(QGraphicsPathItem):
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.start_port._connections.append(self)
        self.end_port._connections.append(self)
        self.setZValue(-1)
        self._update_path()
        
    def _update_path(self):
        # Create a curved path between ports
        path = QPainterPath()
        start_pos = self.start_port.get_socket_position()
        end_pos = self.end_port.get_socket_position()
        
        path.moveTo(start_pos)
        
        # Calculate control points for a curved line
        dx = end_pos.x() - start_pos.x()
        dy = end_pos.y() - start_pos.y()
        
        ctrl1 = QPointF(start_pos.x() + dx * 0.5, start_pos.y())
        ctrl2 = QPointF(start_pos.x() + dx * 0.5, end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, end_pos)
        
        self.setPath(path)
        self.setPen(QPen(QColor(200, 200, 200, 200), 2))
        
    def update_path_from_ports(self):
        self._update_path()
        
    def disconnect(self):
        if self in self.start_port._connections:
            self.start_port._connections.remove(self)
        if self in self.end_port._connections:
            self.end_port._connections.remove(self)
        if self.scene():
            self.scene().removeItem(self)