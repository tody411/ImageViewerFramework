
# -*- coding: utf-8 -*-
## @package npr_sfs.ui.glwidget
#
#  npr_sfs.ui.glwidget utility package.
#  @author      tody
#  @date        2015/10/16


import sys
import math

import numpy as np
from PyQt4 import QtCore, QtGui, QtOpenGL

from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.ui.tool.camera_tool import CameraTool3D
from ivf.scene.gl3d.camera import PerspectiveCamera, lookAtBoundingBox
from ivf.scene.gl3d.image_plane import TexturePlane, ImagePlane


class GLView(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)

        self.setAutoFillBackground(False)
        self.setMinimumSize(300, 300)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAcceptDrops(True)

    def initializeGL(self):
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glClearColor(0.2, 0.4, 0.8, 1.0)
        glClearDepth(1.0)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._renderBackGround()

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        aspect = width / float(height)
        glMatrixMode ( GL_PROJECTION )
        glLoadIdentity()
        glOrtho ( -aspect , aspect , -1 , 1 , -10.0 , 10.0 )
        glMatrixMode ( GL_MODELVIEW )
        #PerspectiveCamera(30.0, aspect, 1.0, 1000.0).gl()

    def unproject(self, p_xy):
        projection_mat = glGetDouble(GL_PROJECTION_MATRIX)
        modelview_mat = glGetDouble(GL_MODELVIEW_MATRIX)

        viewport = glGetIntegerv(GL_VIEWPORT)

        p_near = np.array(gluUnProject(p_xy[0], viewport[3] - p_xy[1], 0.0, modelview_mat, projection_mat, viewport))
        p_far = np.array(gluUnProject(p_xy[0], viewport[3] - p_xy[1], 1.0, modelview_mat, projection_mat, viewport))
        ray = p_far - p_near

        p = p_near - (p_near[2] / ray[2]) * ray

        return p_near, ray

    def _renderBackGround(self):
        self.width()
        aspect = self.width() / float(self.height())
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        glBegin(GL_QUADS)
        glColor3f(0.1, 0.1, 0.1)
        glVertex3f(-aspect, -1.0, -9.0)

        glColor3f(0.1, 0.1, 0.1)
        glVertex3f(aspect, -1.0, -9.0)

        glColor3f(0.5, 0.6, 0.7)
        glVertex3f(aspect, 1.0, -9.0)

        glColor3f(0.5, 0.6, 0.7)
        glVertex3f(-aspect, 1.0, -9.0)
        glEnd()
        glColor3f(1.0, 1.0, 1.0)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    view = GLView()
    view.show()
    sys.exit(app.exec_())