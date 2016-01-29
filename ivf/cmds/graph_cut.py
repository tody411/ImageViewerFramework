
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
from ivf.cv.image import rgb, to8U
from ivf.scene.layer import Layer


class GraphCutCommand(BaseCommand):
    def __init__(self, scene, view, parent=None):
        super(GraphCutCommand, self).__init__(scene, "GraphCut", parent)
        self._view = view
        self._tool = StrokeTool()
        self._tool.setStrokeEditedCallBack(self._strokeEdited)

    def _runImp(self):
        stroke_sets = self._scene.strokeSets()
        self._tool.setStrokeSets(stroke_sets)
        self._view.setTool(self._tool)

    def _strokeEdited(self, stroke_sets):
        print "Graph Cut Command"
        if len(stroke_sets.strokeSets()) < 2:
            return

        fg_stroke_set, bg_stroke_set = stroke_sets.strokeSets()[:2]

        image = self._scene.image()

        image_rgb = to8U(rgb(image))

        mask = np.zeros(image.shape[:2], dtype=np.uint8)
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

        cv2.grabCut(image_rgb, mask, None, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)

        fg_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        fg_mask[(mask==int(cv2.GC_FGD)) | (mask==int(cv2.GC_PR_FGD))] = 255

        bg_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        bg_mask[(mask==int(cv2.GC_BGD)) | (mask==int(cv2.GC_PR_BGD))] = 255

        layer_set = self._scene.layerSet()
        layer_set.clear()
        layer_set.addLayer(Layer(name="BG", color=(0.0, 0.0, 1.0, 0.4), mask=bg_mask))
        layer_set.addLayer(Layer(name="FG", color=(1.0, 0.0, 0.0, 0.4), mask=fg_mask))
