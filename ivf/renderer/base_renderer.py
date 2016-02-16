
# -*- coding: utf-8 -*-
## @package npr_sfs.shading_evaluation.renderer.base_renderer
#
#  npr_sfs.shading_evaluation.renderer.base_renderer utility package.
#  @author      tody
#  @date        2015/12/06


from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *

from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *
from ivf.scene.gl3d.texture import RenderedTexture


class BaseRenderer(object):
    ## Constructor
    def __init__(self):
        self._name = ""
        self._viewport = None
        self._renderbuffer = None

    def bind(self):
        if self._renderbuffer is None:
            return
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        self._renderbuffer.bind()
        glViewport(0, 0,
                     self._renderbuffer.size().width(),
                     self._renderbuffer.size().height())
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glColorMask(True, True, True, True)
        glClear(GL_COLOR_BUFFER_BIT)

    def unbind(self):
        if self._renderbuffer is None:
            return
        self._renderbuffer.release()
        glPopAttrib()

    def render(self, offline=False):
        if offline:
            self.bind()
        self._render(offline)
        if offline:
            self.unbind()

    def _render(self, offline=False):
        pass

    def _viewQuads(self):
        glBegin(GL_QUADS)

        glTexCoord2f(0.0, 1.0)
        glVertex2f(-1.0, -1.0)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-1.0,  1.0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(1.0, 1.0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(1.0, -1.0)

        glEnd()

    def _imageQuads(self):
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

    def setViewport(self, viewport=QSize()):
        self._viewport = viewport
        self._updateViewportFrameBuffer()

    def bindTexture(self):
        if self._renderbuffer is not None:
            return
        glBindTexture(GL_TEXTURE_2D, self._renderbuffer.texture())

    def renderedTexture(self):
        return RenderedTexture(self._renderbuffer)

    def _updateViewportFrameBuffer(self):
        if self._viewport is None:
            return

        if self._renderbuffer is not None:
            if self._viewport == self._renderbuffer.size():
                return
            del self._renderbuffer
        else:
            self._renderbuffer = QGLFramebufferObject(self._viewport)
