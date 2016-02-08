# -*- coding: utf-8 -*-
## @package ivf.core.shader.shader
#
#  ivf.core.shader.shader utility package.
#  @author      tody
#  @date        2016/02/07


class Shader(object):
    def __init__(self):
        super(Shader, self).__init__()

    def diffuseTerm(self, L, N_32F):
        return 0

    def diffuseShading(self, L, N_32F):
        return 0

    def specularTerm(self):
        return 0

    def specularShading(self):
        return 0


