# -*- coding: utf-8 -*-
## @package ivf.core.sfs.colormap_sphere
#
#  ivf.core.sfs.colormap_sphere utility package.
#  @author      tody
#  @date        2016/02/19
from ivf.core.shader.light_sphere import normalSphere
from ivf.core.shader.toon import ColorMapShader
from ivf.cv.image import setAlpha, to8U


def colorMapSphere(L, M_32F, h=512, w=512):
    N_32F, A_32F = normalSphere(h=h, w=w)
    C_32F = ColorMapShader(M_32F).diffuseShading(L, N_32F)
    C_32F = setAlpha(C_32F, A_32F)
    return C_32F
