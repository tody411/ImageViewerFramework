import numpy as np

import lambert
from ivf.np.norm import normalizeVector
from ivf.core.shader.shader import Shader
from ivf.core.shader.lambert import LambertShader
from ivf.core.shader.half_lambert import HalfLambertShader


class ToonShader(Shader):
    def __init__(self, borders=[0.5, 0.9], colors=[np.array([0.2, 0.2, 0.5]),
                                              np.array([0.3, 0.3, 0.6]),
                                              np.array([0.5, 0.5, 0.8])]):
        super(ToonShader, self).__init__()
        self._borders = borders
        self._colors = colors

    def diffuseTerm(self, L, N_32F):
        return HalfLambertShader(ka=np.zeros(3), kd=np.zeros(3)).diffuseTerm(L, N_32F)

    def diffuseShading(self, L, N_32F):
        I_32F = self.diffuseTerm(L, N_32F)

        h, w, cs = N_32F.shape

        C_32F = np.zeros((h, w, cs), dtype=np.float32)
        I_32F_flat = I_32F.reshape(h * w)
        C_32F_flat = C_32F.reshape(-1, 3)

        colors = self._colors
        borders = self._borders

        C_32F_flat[:, :] = colors[0]

        for border, color in zip(borders, colors[1:]):
            C_32F_flat[I_32F_flat > border, :] = color

        return C_32F

## Compute illumination for the normal image and light direction.
#  Illumination value will be in [0, 1].
def diffuse(N_32F, L, borders=[0.5], colors=[np.array([0.2, 0.2, 0.5]), np.array([0.5, 0.5, 0.8])]):
    L = normalizeVector(L)
    print L
    I_32F = lambert.diffuse(N_32F, L)

    h, w, cs = N_32F.shape

    C_32F = np.zeros((h, w, cs), dtype=np.float32)
    I_32F_flat = I_32F.reshape(h * w)
    C_32F_flat = C_32F.reshape(-1, 3)

    C_32F_flat[:, :] = colors[0]

    for border, color in zip(borders, colors[1:]):
        C_32F_flat[I_32F_flat > border, :] = color

    return C_32F