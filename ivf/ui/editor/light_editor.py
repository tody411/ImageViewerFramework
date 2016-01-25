# -*- coding: utf-8 -*-
## @package npr_sfs.ui.editor.light_editor
#
#  npr_sfs.ui.editor.light_editor utility package.
#  @author      tody
#  @date        2015/11/17

import numpy as np

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.shaders.shader_program import ShaderProgram
from ivf.ui.glview import GLView


class LightDirEditor(GLView):

    ## Constructor
    def __init__(self):
        super(LightDirEditor, self).__init__()
        self._lambert_shader = None
        self.setMaximumSize(128, 128)

    def initializeGL(self):
        glClearColor(0.8, 0.8, 1.0, 0.0)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

        glClearColor(0.2, 0.4, 0.8, 1.0)
        glClearDepth(1.0)

        self._lambert_shader = ShaderProgram("SimpleTransformTexture.vert", "LightEditShader.frag")
        self.setLightData(np.array([0.0, 0.0, 1.0]))

    def paintGL(self):
        glColorMask(True, True, True, True)
        glClear(GL_COLOR_BUFFER_BIT)

        self._lambert_shader.bind()

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

        self._lambert_shader.release()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glLoadIdentity()

    def mousePressEvent(self, e):
        pass

    def mouseMoveEvent(self, e):
        if not e.buttons() & Qt.LeftButton:
            return
        p = self._numpy_position(e)
        Lx = 2.0 * p[0] / float(self.size().width()) - 1.0
        Ly = - (2.0 * p[1] / float(self.size().height()) - 1.0)
        r = np.linalg.norm(np.array([Lx, Ly]))
        Lz = np.sqrt(max(0.0, 1.0 - r))
        L = np.array([Lx, Ly, Lz])
        L /= np.linalg.norm(L)
        self.setLightData(L)
        self.updateGL()

    def setLightData(self, L):
        lightNo = 0
        glLightAmb = [0.1, 0.1, 0.1, 1.0]
        glLghtDif = [0.8, 0.8, 0.8, 1.0]
        glLightSpec = [0.0, 0.0, 0.0, 1.0]
        glLightPos = [L[0], L[1], L[2], 0.0]
        glEnable(GL_LIGHT0 + lightNo)
        glLightfv(GL_LIGHT0 + lightNo, GL_AMBIENT, glLightAmb)
        glLightfv(GL_LIGHT0 + lightNo, GL_DIFFUSE, glLghtDif)
        glLightfv(GL_LIGHT0 + lightNo, GL_SPECULAR, glLightSpec)
        glLightfv(GL_LIGHT0 + lightNo, GL_POSITION, glLightPos)

    def _qpoint_to_numpy(self, qp):
        return np.array([qp.x(), qp.y()])

    def _numpy_position(self, e):
        pos = e.pos()
        return self._qpoint_to_numpy(pos)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    window = LightDirEditor()
    window.show()
    sys.exit(app.exec_())