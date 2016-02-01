

# -*- coding: utf-8 -*-
## @package npr_sfs.scene.texture
#
#  npr_sfs.scene.texture utility package.
#  @author      tody
#  @date        2015/10/17

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from npr_sfs.cv.image import to8U


class Texture:
    ## Constructor
    def __init__(self):
        self._image = None
        self._texture_id = None
        self._wrap_S = GL_CLAMP
        self._wrap_T = GL_CLAMP

    def setImage(self, image):
        self._image = to8U(image)

    def gl(self):
        glEnable(GL_TEXTURE_2D)

        if self._texture_id is None:
            self._texture_id = glGenTextures(1)

        if self._image is None:
            return

        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self._wrap_S)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self._wrap_T)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, self._image.shape[1],
                          self._image.shape[0], GL_RGBA, GL_UNSIGNED_BYTE, self._image)


class RenderedTexture:
    ## Constructor
    def __init__(self, renderbuffer):
        self._renderbuffer = renderbuffer

    def gl(self):
        if self._renderbuffer is None:
            return
        glBindTexture(GL_TEXTURE_2D, self._renderbuffer.texture())