
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


class GLView(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)

        self.setMinimumSize(300, 300)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAcceptDrops(True)

    def initializeGL(self):
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glClearColor(0.2, 0.4, 0.8, 1.0)
        glClearDepth(1.0)


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        aspect = width / float(height)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    view = GLView()
    view.show()
    sys.exit(app.exec_())