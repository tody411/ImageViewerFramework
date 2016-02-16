# -*- coding: utf-8 -*-
## @package ivf.core.shader.shader
#
#  ivf.core.shader.shader utility package.
#  @author      tody
#  @date        2016/02/07

import numpy as np
from ivf.np.norm import normalizeVector


def LdotN(L, N_32F):
    L = normalizeVector(L)
    h, w = N_32F.shape[:2]
    N_flat = N_32F.reshape((-1, 3))
    LdN_flat = np.dot(N_flat, L)
    LdN = LdN_flat.reshape(h, w)
    return LdN


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


