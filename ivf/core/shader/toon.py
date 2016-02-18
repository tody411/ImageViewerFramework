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


class ColorMapShader(Shader):
    def __init__(self, M_32F, k_a=0.4):
        super(ColorMapShader, self).__init__()
        self._k_a = k_a
        self._M_32F = M_32F.reshape(-1, 3)

    def diffuseTerm(self, L, N_32F):
        return HalfLambertShader(ka=np.zeros(3), kd=np.zeros(3)).diffuseTerm(L, N_32F)

    def diffuseShading(self, L, N_32F):
        I_32F = self.diffuseTerm(L, N_32F)

        I_min, I_max = np.min(I_32F), np.max(I_32F)
        I_min = self._k_a

        map_size = self._M_32F.shape[0]
        I_ids = (map_size - 1) * (I_32F - I_min) / (I_max - I_min)
        I_ids = np.int32(I_ids)
        I_ids = np.clip(I_ids, 0, map_size - 1)

        C_32F = self._M_32F[I_ids, :]

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