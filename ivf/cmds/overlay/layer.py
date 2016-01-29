
# -*- coding: utf-8 -*-
## @package ivf.cmds.overlay.layer
#
#  ivf.cmds.overlay.layer utility package.
#  @author      tody
#  @date        2016/01/27


from PyQt4.QtGui import *
from PyQt4.QtCore import *

import numpy as np

from ivf.cmds.overlay.overlay_cmd import OverlayCommand


class LayerOverlayCommand(OverlayCommand):
    def __init__(self, scene, view, parent=None):
        super(LayerOverlayCommand, self).__init__(scene, view, "Layer", parent)

    def _imageOverlayImp(self, image):
        layer_set = self._scene.layerSet()

        for layer in layer_set.layers():
            color = layer.color()
            mask = layer.mask()
            color = 255 * np.array(color)
            image[mask>0, :3] = color[:3]
        return image


