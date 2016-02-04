
# -*- coding: utf-8 -*-
## @package ivf.cmds.sparse_interpolation.sparse_sampling
#
#  ivf.cmds.sparse_interpolation.sparse_sampling utility package.
#  @author      tody
#  @date        2016/02/03


import cv2

from ivf.cmds.base_cmds import BaseCommand

from ivf.core.sparse_interpolation.sparse_sampling import sparseSampling


class SparseSamplingCommand(BaseCommand):
    def __init__(self, scene, parent=None):
        super(SparseSamplingCommand, self).__init__(scene, "Sparse Sampling", parent)

    def _runImp(self):
        image = self._scene.image()
        h, w = image.shape[:2]
        map_image = sparseSampling(image)
        self._scene.setImage(map_image)