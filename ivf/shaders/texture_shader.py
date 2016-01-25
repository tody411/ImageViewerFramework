# -*- coding: utf-8 -*-
## @package npr_sfs.shaders.texture_shader
#
#  npr_sfs.shaders.texture_shader utility package.
#  @author      tody
#  @date        2015/11/17

from ivf.shaders.shader_program import ShaderProgram


class TextureShader(ShaderProgram):
    def __init__(self, vertex_shader, fragment_shader):
        super(TextureShader, self).__init__(vertex_shader, fragment_shader)

    def _initAttr(self):
        super(TextureShader, self)._initAttr()
        texLocation = self._program.uniformLocation("tex")
        self._program.setUniformValue(texLocation, 0)