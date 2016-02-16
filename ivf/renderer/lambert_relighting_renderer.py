
# -*- coding: utf-8 -*-
## @package npr_sfs.shading_evaluation.renderer.lambert_relighting_renderer
#
#  npr_sfs.shading_evaluation.renderer.lambert_relighting_renderer utility package.
#  @author      tody
#  @date        2015/12/06


from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.renderer.base_renderer import BaseRenderer
from ivf.shaders.shader_program import ShaderProgram


class LambertRelightingRenderer(BaseRenderer):
    ## Constructor
    def __init__(self):
        super(LambertRelightingRenderer, self).__init__()

        self._shader = None
        self._color_texture = None
        self._normal_texture = None

    def initializeGL(self):
        self._shader = ShaderProgram("SimpleTransformTexture.vert", "LambertRelightingShader.frag")
        self._shader.setUniformValue("normalTex", 0)
        self._shader.setUniformValue("colorTex", 1)

    def setNormalTexture(self, normal_texture):
        self._normal_texture = normal_texture

    def setColorTexture(self, color_texture):
        self._color_texture = color_texture

    def _render(self, offline=False):
        self._shader.bind()

        glActiveTexture(GL_TEXTURE0)
        self._normal_texture.gl()
        glActiveTexture(GL_TEXTURE1)
        self._color_texture.gl()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._viewQuads()

        glFlush()

        self._shader.release()