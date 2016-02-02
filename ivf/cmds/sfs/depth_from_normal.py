
# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.depth_from_normal
#
#  ivf.cmds.sfs.depth_from_normal utility package.
#  @author      tody
#  @date        2016/02/01

import numpy as np
import cv2

from ivf.cmds.base_cmds import BaseCommand

from ivf.cv.image import alpha
from ivf.core.sfs.lumo import estimateNormal
from ivf.scene.scene import Scene
from ivf.core.sfs.depth_from_normal import depthFromNormal


class DepthFromNormalCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(DepthFromNormalCommand, self).__init__(scene, "Depth From Normal", parent)

    def _runImp(self):
        image = self._scene.image()
        A_8U = alpha(image)

        if A_8U is None:
            return

        N_32F = self._scene.normal()

        if N_32F is None:
            return

        h_high, w_high = image.shape[:2]
        w_low = min(256, w_high)
        h_low = w_low * h_high / w_high

        N_32F = cv2.resize(N_32F, (w_low, h_low))
        A_8U = cv2.resize(A_8U, (w_low, h_low))

        D_32F = depthFromNormal(N_32F, A_8U)

        d_scale = w_high / float(w_low)
        D_32F = d_scale * D_32F

        D_32F = cv2.resize(D_32F, (w_high, h_high))

        self._scene.setDepth(D_32F)
        self._scene.setDisplayMode(Scene.DisplayDepth)

        self._output_info = "(%s, %s)" %(np.min(D_32F), np.max(D_32F))

        print self._output_info
