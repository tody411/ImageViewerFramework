
# -*- coding: utf-8 -*-
## @package ivf.cmds.graph_cut
#
#  ivf.cmds.graph_cut utility package.
#  @author      tody
#  @date        2016/01/25

import numpy as np
import cv2

from ivf.cmds.base_cmds import BaseCommand


class GraphCutCommand(BaseCommand):
    def __init__(self, scene):
        super(GraphCutCommand, self).__init__(scene, "GraphCut")

    def _runImp(self):
        image = self._scene.image()

        mask = np.zeros(image.shape[:2], np.uint8)
        mask.fill(cv2.GC_PR_BGD)

        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)

        mask = self._mask
        mask, bgdModel, fgdModel = cv2.grabCut(image, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)