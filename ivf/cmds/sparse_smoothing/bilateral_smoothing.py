
# -*- coding: utf-8 -*-
## @package ivf.cmds.sparse_smoothing.bilateral_smoothing
#
#  ivf.cmds.sparse_smoothing.bilateral_smoothing utility package.
#  @author      tody
#  @date        2016/02/03

import cv2

from ivf.cmds.base_cmds import BaseCommand
from ivf.core.sparse_smoothing.bilateral_smoothing import bilateralSmoothing


class BilateralSmoothingCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(BilateralSmoothingCommand, self).__init__(scene, "Bilateral Smoothing", parent)

    def _runImp(self):
        image = self._scene.image()
        h, w = image.shape[:2]
        w_low = 512
        h_low = w_low * h / w
        image_low = cv2.resize(image, (w_low, h_low))

        image_smooth_low = bilateralSmoothing(image_low)
        image_smooth = cv2.resize(image_smooth_low, (w, h))

        self._scene.setImage(image_smooth)
