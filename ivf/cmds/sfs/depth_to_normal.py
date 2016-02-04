
# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.depth_to_normal
#
#  ivf.cmds.sfs.depth_to_normal utility package.
#  @author      tody
#  @date        2016/02/04


import numpy as np
import cv2

from ivf.cmds.base_cmds import BaseCommand

from ivf.core.sfs.depth_to_normal import depthToNormal


class DepthToNormalCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(DepthToNormalCommand, self).__init__(scene, "Depth To Normal", parent)

    def _runImp(self):
        image = self._scene.image()

        D_32F = self._scene.depth()

        if D_32F is None:
            return

        N_32F = depthToNormal(D_32F)
        self._scene.setNormal(N_32F)