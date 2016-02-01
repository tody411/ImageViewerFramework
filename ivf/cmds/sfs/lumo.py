
# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.lumo
#
#  ivf.cmds.sfs.lumo utility package.
#  @author      tody
#  @date        2016/02/01

import cv2

from ivf.cmds.base_cmds import BaseCommand

from ivf.cv.image import alpha
from ivf.core.sfs.lumo import estimateNormal
from ivf.scene.scene import Scene


class LumoCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(LumoCommand, self).__init__(scene, "Lumo", parent)

    def _runImp(self):
        image = self._scene.image()
        A_8U = alpha(image)

        if A_8U is None:
            return

        A_8U = cv2.resize(A_8U, None, fx=0.25, fy=0.25)
        N0_32F, N_32F = estimateNormal(A_8U)

        h, w = image.shape[:2]
        N_32F = cv2.resize(N_32F, (w, h))
        self._scene.setNormal(N_32F)
        self._scene.setDisplayMode(Scene.DisplayNormal)
