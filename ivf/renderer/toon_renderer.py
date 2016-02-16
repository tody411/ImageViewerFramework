# -*- coding: utf-8 -*-
## @package npr_sfs.shading_evaluation.renderer.toon_renderer
#
#  npr_sfs.shading_evaluation.renderer.toon_renderer utility package.
#  @author      tody
#  @date        2015/12/06

from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL import *

from ivf.renderer.base_renderer import BaseRenderer
from ivf.shaders.shader_program import ShaderProgram


class ToonRenderer(BaseRenderer):
    ## Constructor
    def __init__(self):
        super(ToonRenderer, self).__init__()

        self._shader = None
        self._color_map_texture = None
        self._normal_texture = None

    def initializeGL(self):
        self._shader = ShaderProgram("SimpleTransformTexture.vert", "ToonShader.frag")
        self._shader.setUniformValue("normalTex", 0)
        self._shader.setUniformValue("colorMapTex", 1)

    def setNormalTexture(self, normal_texture):
        self._normal_texture = normal_texture

    def setColorMapTexture(self, color_map_texture):
        self._color_map_texture = color_map_texture

    def _render(self, offline=False):
        self._shader.bind()
        glActiveTexture(GL_TEXTURE0)
        self._normal_texture.gl()
        glActiveTexture(GL_TEXTURE1)
        self._color_map_texture.gl()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if offline:
            self._imageQuads()
        else:
            self._viewQuads()

        glFlush()

        self._shader.release()