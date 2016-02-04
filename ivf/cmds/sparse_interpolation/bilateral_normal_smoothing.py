
# -*- coding: utf-8 -*-
## @package ivf.cmds.sparse_interpolation.bilateral_normal_smoothing
#
#  ivf.cmds.sparse_interpolation.bilateral_normal_smoothing utility package.
#  @author      tody
#  @date        2016/02/03



import cv2

from ivf.cmds.base_cmds import BaseCommand
from ivf.core.sparse_interpolation.bilateral_normal_smoothing import bilateralNormalSmoothing

from ivf.scene.scene import Scene


class BilateralNormalSmoothingCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(BilateralNormalSmoothingCommand, self).__init__(scene, "Bilateral Normal Smoothing", parent)

    def _runImp(self):
        image = self._scene.image()
        normal = self._scene.normal()
        h, w = image.shape[:2]
        w_low = 256
        h_low = w_low * h / w
        image_low = cv2.resize(image, (w_low, h_low))
        normal_low = cv2.resize(normal, (w_low, h_low))

        normal_smooth_low = bilateralNormalSmoothing(image_low, normal_low)
        normal_smooth = cv2.resize(normal_smooth_low, (w, h))

        self._scene.setNormal(normal_smooth)
        self._scene.setDisplayMode(Scene.DisplayNormal)
