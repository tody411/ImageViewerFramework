
# -*- coding: utf-8 -*-
## @package npr_sfs.ui.tool.drag_tool
#
#  npr_sfs.ui.tool.drag_tool utility package.
#  @author      tody
#  @date        2015/10/27


import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from npr_sfs.ui.tool.base_tool import BaseTool


class DragTool(BaseTool):
    outPoint = pyqtSignal(object)

    ## Constructor
    def __init__(self):
        super(DragTool, self).__init__()

        self._drag_point = None

        self._pen = QPen(QColor(255, 0, 0, 100))
        self._pen.setWidth(2)
        self._pen.setCapStyle(Qt.RoundCap)

    def setPointSize(self, point_size):
        self._pen.setWidth(point_size)

    def setPoint(self, p):
        self._drag_point = p
        self._view.update()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:

            self._drag_point = self._mousePosition(e)
            self.outPoint.emit(self._drag_point)
            self._view.update()

    def _overlayFunc(self, painter):
        if self._drag_point is None:
            return

        painter.setPen(self._pen)

        p = self._drag_point
        painter.drawPoint(QPoint(p[0], p[1]))
