
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
from ivf.ui.qimage_util import ndarrayToQImage


class LayerOverlayCommand(OverlayCommand):
    def __init__(self, scene, view, parent=None):
        super(LayerOverlayCommand, self).__init__(scene, view, "Layer", parent)

    def _imageOverlayImp(self):
        scene_image = self._scene.image()
        h, w = scene_image.shape[:2]
        overlay_image = np.zeros((h, w, 4), dtype=np.uint8)
        layer_set = self._scene.layerSet()

        for layer in layer_set.layers():
            color = layer.color()
            mask = layer.mask()
            color = 255 * np.array(color)
            overlay_image[mask>0, :] = color

        return ndarrayToQImage(overlay_image)


