
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

        N_32F = cv2.resize(N_32F, None, fx=0.25, fy=0.25)
        h, w = N_32F.shape[:2]
        A_8U = cv2.resize(A_8U, (w, h))

        D_32F = depthFromNormal(N_32F, A_8U)

        h, w = image.shape[:2]
        D_32F = cv2.resize(D_32F, (w, h))

        print D_32F.dtype

        self._scene.setDepth(D_32F)
        self._scene.setDisplayMode(Scene.DisplayDepth)

        self._output_info = "(%s, %s)" %(np.min(D_32F), np.max(D_32F))

        print self._output_info
