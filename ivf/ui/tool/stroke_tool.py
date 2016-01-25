# -*- coding: utf-8 -*-
## @package npr_sfs.ui.tool.stroke_tool
#
#  npr_sfs.ui.tool.stroke_tool utility package.
#  @author      tody
#  @date        2015/10/26

import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.ui.tool.base_tool import BaseTool


class StrokeTool(BaseTool):
    ## Constructor
    def __init__(self):
        super(StrokeTool, self).__init__()
        self._strokes = []
        self._stroke_edited_func = None
        self._adjusting_brush = False
        self._p_old = None
        self._brush_size = 20

    def setStrokeEditedCallBack(self, stroke_edited_func):
        self._stroke_edited_func = stroke_edited_func

    def setStrokes(self, strokes):
        self._strokes = strokes
        self._view.update()

    def setView(self, view):
        super(StrokeTool, self).setView(view)

    def mousePressEvent(self, e):
        self._p_old = self._mousePosition(e)
        if self._adjusting_brush:
            return

        if e.buttons() & Qt.LeftButton:
            if (e.modifiers() & Qt.ShiftModifier):
                self._strokes.append([])
            else:
                self._strokes = [[]]

            self.addStrokePoint(e)

    def mouseReleaseEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            if self._adjusting_brush:
                self.adjustBrush(e)
                return

            if self._addingStrokePoint(e):
                self.addStrokePoint(e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_B:
            self._adjusting_brush = True

    def keyReleaseEvent(self, e):
        self._adjusting_brush = False

    def adjustBrush(self, e):
        p = self._mousePosition(e)
        dx = p[0] - self._p_old[0]

        self._brush_size += dx
        self._brush_size = max(3, self._brush_size)

        self._p_old = p

        self._view.update()

    def addStrokePoint(self, e):
        p = self._mousePosition(e)
        self._strokes[-1].append(p)
        self._view.update()

        if self._stroke_edited_func:
            self._stroke_edited_func(self._strokes)

    def _addingStrokePoint(self, e):
        p = self._mousePosition(e)
        if len(self._strokes[-1]) == 0:
            return True

        p_old = self._strokes[-1][-1]

        if np.linalg.norm(p - p_old) > 5:
            return True

        return False

    def _overlayFunc(self, painter):
        if len(self._strokes) == 0:
            return

        pen = QPen(QColor(255, 0, 0, 100))
        pen.setWidth(self._brush_size)
        pen.setCapStyle(Qt.RoundCap);
        painter.setPen(pen)

        p = self._p_old
        painter.drawPoint(QPoint(p[0], p[1]))

        for stroke in self._strokes:
            polyline = QPolygon([QPoint(p[0], p[1]) for p in stroke])
            painter.drawPolyline(polyline)
