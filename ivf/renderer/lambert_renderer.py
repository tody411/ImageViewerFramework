
# -*- coding: utf-8 -*-
## @package npr_sfs.shading_evaluation.renderer.lambert_renderer
#
#  npr_sfs.shading_evaluation.renderer.lambert_renderer utility package.
#  @author      tody
#  @date        2015/12/06


from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.renderer.base_renderer import BaseRenderer
from ivf.shaders.shader_program import ShaderProgram


class LambertRenderer(BaseRenderer):
    ## Constructor
    def __init__(self):
        super(LambertRenderer, self).__init__()

        self._shader = None
        self._normal_texture = None

    def initializeGL(self):
        self._shader = ShaderProgram("SimpleTransformTexture.vert", "LambertShader.frag")
        self._shader.setUniformValue("normalTex", 0)

    def setNormalTexture(self, normal_texture):
        self._normal_texture = normal_texture

    def _render(self, offline=False):
        self._shader.bind()
        glActiveTexture(GL_TEXTURE0)
        self._normal_texture.gl()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._viewQuads()

        glFlush()

        self._shader.release()