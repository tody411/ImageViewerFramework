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
from ivf.scene.stroke import StrokeSet, StrokeSets


class StrokeTool(BaseTool):
    ## Constructor
    def __init__(self):
        super(StrokeTool, self).__init__()
        self._stroke_sets = StrokeSets()
        self._stroke_sets.addStrokeSet("1", color=(1.0, 0.0, 0.0, 0.4))

        self._stroke_edited_func = None
        self._stroke_updated_func = None
        self._adjusting_brush = False
        self._p_old = None
        self._brush_size = 20

    def setStrokeSets(self, stroke_sets):
        self._stroke_sets = stroke_sets
        self._selectStrokeSet("1", color=(1.0, 0.0, 0.0, 0.4))

    def setStrokeEditedCallBack(self, stroke_edited_func):
        self._stroke_edited_func = stroke_edited_func

    def setStrokeUpdatedCallBack(self, stroke_updated_func):
        self._stroke_updated_func = stroke_updated_func

    def setView(self, view):
        super(StrokeTool, self).setView(view)

    def mousePressEvent(self, e):
        self._p_old = self._mousePosition(e)
        if self._adjusting_brush:
            return

        if e.buttons() & Qt.LeftButton:
            if (e.modifiers() & Qt.ShiftModifier):
                self._stroke_sets.selectedStrokeSet().addEmptyStroke()

            else:
                self._stroke_sets.selectedStrokeSet().clear(with_empty=True)

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

        if e.key() == Qt.Key_0:
            self._selectStrokeSet("0", (0.0, 0.0, 1.0, 0.4))

        if e.key() == Qt.Key_1:
            self._selectStrokeSet("1", (1.0, 0.0, 0.0, 0.4))

        if e.key() == Qt.Key_2:
            self._selectStrokeSet("2", (0.0, 1.0, 0.0, 0.4))

        if e.key() == Qt.Key_3:
            self._selectStrokeSet("3", (1.0, 1.0, 0.0, 0.4))

        if e.key() == Qt.Key_4:
            self._selectStrokeSet("4", (1.0, 0.0, 1.0, 0.4))

        if e.key() == Qt.Key_5:
            self._selectStrokeSet("5", (0.0, 1.0, 1.0, 0.4))

        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            print "Press Enter"
            if self._stroke_edited_func:
                self._stroke_edited_func(self._stroke_sets)

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
        self._stroke_sets.selectedStrokeSet().lastStroke().addStrokePoint(p, self._brush_size)

        self._view.update()

        if self._stroke_updated_func:
            self._stroke_updated_func(self._stroke_sets)

    def _addingStrokePoint(self, e):
        p = self._mousePosition(e)
        if self._stroke_sets.selectedStrokeSet().lastStroke().empty() == 0:
            return True

        p_old = self._stroke_sets.selectedStrokeSet().lastStroke().points()[-1]

        if np.linalg.norm(p - p_old) > 3:
            return True

        return False

    def _overlayFunc(self, painter):
        pen = QPen(QColor(255, 0, 0, 100))
        pen.setWidth(self._brush_size)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        p = self._p_old
        painter.drawPoint(QPoint(p[0], p[1]))

        for stroke_set in self._stroke_sets.strokeSets():
            color = stroke_set.color()
            for stroke in stroke_set.strokes():
                brush_size = stroke.brushSize()

                pen = QPen(QColor.fromRgbF(color[0], color[1], color[2], color[3]))
                pen.setWidth(brush_size)

                painter.setPen(pen)
                polyline = QPolygon([QPoint(p[0], p[1]) for p in stroke.points()])
                painter.drawPolyline(polyline)

    def _selectStrokeSet(self, name, color):
        if self._stroke_sets.selectStrokeSet(name):
            return
        self._stroke_sets.addStrokeSet(name, color)
