
# -*- coding: utf-8 -*-
## @package ivf.ui.model_view
#
#  ivf.ui.model_view utility package.
#  @author      tody
#  @date        2016/02/04

import numpy as np

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.ui.glview import GLView
from ivf.ui.tool.camera_tool import CameraTool3D
from ivf.scene.gl3d.camera import PerspectiveCamera, lookAtBoundingBox
from ivf.scene.gl3d.image_plane import TexturePlane, ImagePlane


class ModelView(GLView):

    ## Constructor
    def __init__(self, parent=None):
        super(ModelView, self).__init__(parent)
        self._camera_tool = CameraTool3D()
        self._focus_gl = None
        self._model = None
        self._return_func = None

    def setReturnCallback(self, return_func):
        self._return_func = return_func

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._renderBackGround()

        glLoadIdentity()
        self._camera_tool.gl()

        if self._focus_gl is not None:
            self._focus_gl()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)

        if self._model is not None:
            self._model.gl()

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        aspect = width / float(height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-aspect, aspect, -1, 1, -10.0, 10.0)
        glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self._camera_tool.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self._camera_tool.mouseMoveEvent(event)
        self.updateGL()

    def wheelEvent(self, event):
        self._camera_tool.wheelEvent(event)
        self.updateGL()

    def keyPressEvent (self, event):
        self._camera_tool.keyPressEvent(event)

        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self._return_func is not None:
                self._return_func()

        self.updateGL()

    def setModel(self, model):
        self._model = model
        bb = model.boundingBox()
        self._focus_gl = lookAtBoundingBox(bb)

    def setRGBAD(self, RGBA_8U, D_32F):
        model = ImagePlane(RGBA_8U)
        if D_32F is not None:
            model.setDepth(D_32F)
        self.setModel(model)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    view = ModelView()
    view.show()
    sys.exit(app.exec_())