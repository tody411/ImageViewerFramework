
# -*- coding: utf-8 -*-
## @package ivf.ui.editor.normal_editor
#
#  ivf.ui.editor.normal_editor utility package.
#  @author      tody
#  @date        2016/02/08


import numpy as np

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.shaders.shader_program import ShaderProgram
from ivf.ui.glview import GLView


class NormalEditor(GLView):

    ## Constructor
    def __init__(self):
        super(NormalEditor, self).__init__()
        self._normal_shader = None
        self.setMaximumSize(128, 128)
        self._N = np.array([0.0, 0.0, 1.0])

    def setNormal(self, N):
        self._N = N

    def normal(self):
        return self._N

    def initializeGL(self):
        glClearColor(0.8, 0.8, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        #glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glClearColor(0.2, 0.4, 0.8, 1.0)
        glClearDepth(1.0)

        self._normal_shader = ShaderProgram("SimpleTransformTexture.vert", "NormalSphereShader.frag")

    def paintGL(self):
        #glColorMask(True, True, True, True)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._renderBackGround()
        glLoadIdentity()

        self._normal_shader.bind()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)

        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1.0, -1.0)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1.0,  1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(1.0, 1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(1.0, -1.0)

        glEnd()
        glFlush()

        self._normal_shader.release()

        self.drawNormal()

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        glViewport(0, 0, width, height)
        aspect = width / float(height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-aspect, aspect, -1, 1, -10.0, 10.0)

    def mousePressEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        if not e.buttons() & Qt.LeftButton:
            return
        p = self._numpy_position(e)
        Nx = 2.0 * p[0] / float(self.size().width()) - 1.0
        Ny = -(2.0 * p[1] / float(self.size().height()) - 1.0)
        r = np.linalg.norm(np.array([Nx, Ny]))
        Nz = np.sqrt(max(0.001, 1.0 - r * r))
        N = np.array([Nx, Ny, Nz])
        N /= np.linalg.norm(N)
        self.setNormal(N)
        self.updateGL()

    def drawNormal(self, color=[1.0, 0.0, 0.0, 0.5], point_size=10):
        glEnable(GL_POINT_SMOOTH)
        glPointSize(point_size)
        glBegin(GL_POINTS)

        position = self._N
        glColor4f(color[0], color[1], color[2], color[3])
        glVertex3f(position[0], position[1], position[2])
        glEnd()

    def _qpoint_to_numpy(self, qp):
        return np.array([qp.x(), qp.y()])

    def _numpy_position(self, e):
        pos = e.pos()
        return self._qpoint_to_numpy(pos)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    window = NormalEditor()
    window.show()
    sys.exit(app.exec_())