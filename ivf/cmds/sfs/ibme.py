# -*- coding: utf-8 -*-
## @package ivf.cmds.sfs.ibme
#
#  ivf.cmds.sfs.ibme utility package.
#  @author      tody
#  @date        2016/02/01

from ivf.cmds.base_cmds import BaseCommand

from ivf.cv.image import rgb, rgb2gray, to32F
from ivf.core.sfs.ibme import estimateNormal
from ivf.scene.scene import Scene


class IBMECommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(IBMECommand, self).__init__(scene, "ImageBasedMaterialEditing", parent)

    def _runImp(self):
        image = self._scene.image()
        I_32F = to32F(rgb2gray(rgb(image)))
        N_32F, D_32F = estimateNormal(I_32F)
        self._scene.setNormal(N_32F)
        self._scene.setDisplayMode(Scene.DisplayNormal)
