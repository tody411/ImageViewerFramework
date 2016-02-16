
# -*- coding: utf-8 -*-
## @package ivf.core.shader.half_lambert
#
#  ivf.core.shader.half_lambert utility package.
#  @author      tody
#  @date        2016/02/05


import numpy as np

from ivf.np.norm import normalizeVector
from ivf.core.shader.shader import Shader, LdotN


class HalfLambertShader(Shader):
    def __init__(self, ka=np.array([0.0, 0.0, 0.0]), kd=np.array([1.0, 1.0, 1.0])):
        super(HalfLambertShader, self).__init__()
        self._ka = ka
        self._kd = kd

    def diffuseTerm(self, L, N_32F):
        LdN = LdotN(L, N_32F)

        I_32F = 0.5 * LdN + 0.5
        I_32F = np.clip(I_32F, 0.0, 1.0)
        return np.float32(I_32F)

    def diffuseShading(self, L, N_32F):
        I_32F = self.diffuseTerm(L, N_32F)
        h, w = I_32F.shape[:2]
        C_32F = np.zeros((h, w, 3))
        for ci in xrange(3):
            C_32F[:, :, ci] = self._ka[ci] + self._kd[ci] * I_32F
            C_32F = np.clip(C_32F, 0.0, 1.0)
        return np.float32(C_32F)


## Compute illumination for the normal image and light direction.
#  Illumination value will be in [0, 1].
def diffuse(N_32F, L):
    L = normalizeVector(L)
    h, w, cs = N_32F.shape

    N_flat = N_32F.reshape((-1, 3))

    I_flat = np.dot(N_flat, L)
    I_32F = I_flat.reshape((h, w))
    I_32F = 0.5 * I_32F + 0.5
    return np.float32(I_32F)
