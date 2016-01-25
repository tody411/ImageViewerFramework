

# -*- coding: utf-8 -*-
## @package npr_sfs.ui.tool.camera_tool
#
#  npr_sfs.ui.tool.camera_tool utility package.
#  @author      tody
#  @date        2015/10/16

# Numpy modules
import numpy as np

# PyQt modules
from PyQt4.QtGui import *
from PyQt4.QtCore import *

# OpenGL modules
from OpenGL.GL import *
from OpenGL.GLU import *

# Common modules
import math
from ivf.ui.tool.base_tool import BaseTool


## Camera Tool for ImageView.
class CameraTool2D(BaseTool):
    outTransform = pyqtSignal(object)

    ## Constructor
    def __init__(self):
        super(CameraTool2D, self).__init__()
        self._old_pos = np.array([0.0, 0.0])

        self._scale = 1.0
        self._scale_target = 1.0

        self._translation = np.array([0.0, 0.0])
        self._translation_target = np.array([0.0, 0.0])
        self._speed = 0.2

        self._transform = QTransform()

        self._signal_timer = QTimer()
        self._signal_timer.timeout.connect(self.updateTransform)
        self._signal_timer.start(10)

    def setScaleView(self, scale_view):
        self._scale_view = scale_view
        self.outTransform.emit(self.transform())

    def transform(self):
        self._transform.reset()
        self._transform.scale(self._scale, self._scale)
        self._transform.translate(self._translation[0], self._translation[1])
        return self._transform

    def invTransform(self):
        return self._transform.inverted()[0]

    def updateTransform(self):
        ds = self._scale - self._scale_target
        dt = self._translation - self._translation_target
        if np.abs(ds) < 0.01 and np.linalg.norm(dt) < 0.01:
            return

        t = self._speed
        self._scale = (1.0 - t) * self._scale + t * self._scale_target
        self._translation = (1.0 - t) * self._translation + t * self._translation_target

        self.outTransform.emit(self.transform())

    def mousePressEvent(self, e):
        if e.modifiers() & Qt.AltModifier:
            self._old_pos = self._numpy_position(e)

    def mouseReleaseEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.MiddleButton and e.modifiers() & Qt.AltModifier:
            pos = self._numpy_position(e)

            movement = (pos - self._old_pos)

            self._old_pos = pos
            self._translation_target += movement

    def wheelEvent(self, e):
        factor = 2.0 ** (e.delta() / 240.0)

        if self._scale_target < 0.5 and factor < 1.0:
            return

        if self._scale_target > 100 and factor > 1.0:
            return

        scale_new = self._scale_target * factor
        self._scale_target = scale_new

    def keyPressEvent(self, e):
        if e.text() == "f":
            self._translation_target = np.array([0.0, 0.0])
            self._scale_target = 1.0

    def keyReleaseEvent(self, e):
        pass

    def _qpoint_to_numpy(self, qp):
        return np.array([qp.x(), qp.y()])

    def _numpy_position(self, e):
        pos = e.pos()
        return self._qpoint_to_numpy(pos)


class CameraTool3D:
    ## Constructor
    def __init__(self):
        self.reset()

    def reset(self):
        self._scaleXYZ = np.array([1.0, 1.0, 1.0])
        self._scale = 0.0
        self._scalingFactor = 0.001

        self._translateXYZ = [0.0, 0.0, 0.0]
        self._translateFactor = 0.01
        self._rotateXYZ = [0.0, 0.0, 0.0]

        self._rotationFactor = 0.2
        self._rotateSpeedXYZ = [0.0, 0.4, 0.0]

        self._pressPos = [0, 0]

    def gl(self):
        scale = math.pow(2.0, self._scale)

        glTranslate(self._translateXYZ[0], self._translateXYZ[1], self._translateXYZ[2])
        glScale(scale, scale, scale)
        glRotate(self._rotateXYZ[0], 1.0, 0.0, 0.0)
        glRotate(self._rotateXYZ[1], 0.0, 1.0, 0.0)
        glRotate(self._rotateXYZ[2], 0.0, 0.0, 1.0)

    def dxy(self, event):
        dx = event.x() - self._pressPos[0]
        dy = event.y() - self._pressPos[1]

        return np.array([dx, dy])

    def mousePressEvent(self, event):
        if event.modifiers() & Qt.AltModifier:
            self._pressPos = [event.x(), event.y()]

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and event.modifiers() & Qt.AltModifier:
            self.rotateDrag(event)
            self.rotateSpeedDrag(event)
            self._pressPos = [event.x(), event.y()]

        if event.buttons() & Qt.MidButton and event.modifiers() & Qt.AltModifier:
            self.translateDrag(event)
            self._pressPos = [event.x(), event.y()]

    def mouseReleaseEvent(self, event):
        pass

    def wheelEvent(self, event):
        dscale = event.delta() * self._scalingFactor
        self._scale += dscale

    def keyPressEvent (self, event):
        if event.text() == "f":
            self.reset()

    def translateDrag(self, event):
        dxy = self.dxy(event)

        self._translateXYZ[0] += self._translateFactor * dxy[0]
        self._translateXYZ[1] += - self._translateFactor * dxy[1]

    def rotateDrag(self, event):
        dxy = self.dxy(event)

        self._rotateXYZ[0] += self._rotationFactor * dxy[1]
        self._rotateXYZ[1] += self._rotationFactor * dxy[0]

    def rotateSpeedDrag(self, event):
        dxy = self.dxy(event)

        if np.linalg.norm( dxy) > 2.0:
            self._rotateSpeedXYZ = [self._rotationFactor * dxy[1], self._rotationFactor* dxy[0], 0.0]
        else:
            self._rotateSpeedXYZ = [0.0, 0.0, 0.0]

    def animate(self):
        for i in range(3):
            self._rotateXYZ[i] = (self._rotateXYZ[i]  + self._rotateSpeedXYZ[i]) % 360.0
