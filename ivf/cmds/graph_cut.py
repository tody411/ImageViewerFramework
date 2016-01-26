
# -*- coding: utf-8 -*-
## @package ivf.cmds.graph_cut
#
#  ivf.cmds.graph_cut utility package.
#  @author      tody
#  @date        2016/01/25

import numpy as np
import cv2

from ivf.cmds.base_cmds import BaseCommand
from ivf.ui.tool.stroke_tool import StrokeTool
from ivf.cv.image import rgb


class GraphCutCommand(BaseCommand):
    def __init__(self, scene, view, parent=None):
        super(GraphCutCommand, self).__init__(scene, "GraphCut", parent)
        self._view = view
        self._tool = StrokeTool()
        self._tool.setStrokeEditedCallBack(self._strokeEdited)

    def _runImp(self):
        self._view.setTool(self._tool)

    def _strokeEdited(self, stroke_sets):
        print "Graph Cut Command"
        if len(stroke_sets.strokeSets()) < 2:
            return

        fg_stroke_set, bg_stroke_set = stroke_sets.strokeSets()[:2]

        image = self._scene.image()

        image_rgb = rgb(image)

        mask = np.zeros(image.shape[:2], np.uint8)
        mask.fill(cv2.GC_PR_BGD)

        for stroke_set, color in zip([fg_stroke_set, bg_stroke_set],
                                     [int(cv2.GC_FGD), int(cv2.GC_BGD)]):
            for stroke in stroke_set.strokes():
                if stroke.empty():
                    continue
                points = stroke.points()
                points = np.int32(points)

                brush_size = int(stroke.brushSize())

                print color
                cv2.polylines(mask, [points], 0, color, brush_size)

        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)

        cv2.imshow('Input Mask', mask)
        mask, bgdModel, fgdModel = cv2.grabCut(image_rgb, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
        mask[(mask==int(cv2.GC_FGD)) | (mask==int(cv2.GC_PR_FGD))] = 255
        cv2.imshow('Output Mask', mask)
