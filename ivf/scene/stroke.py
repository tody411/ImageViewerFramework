# -*- coding: utf-8 -*-
## @package ivf.scene.stroke
#
#  ivf.scene.stroke utility package.
#  @author      tody
#  @date        2016/01/26

import numpy as np

from ivf.scene.data import Data


class Stroke(Data):
    ## Constructor
    def __init__(self):
        super(Stroke, self).__init__()
        self._points = []
        self._brush_sizes = []

    def empty(self):
        return len(self._points) == 0

    def points(self):
        return self._points

    def brushSize(self):
        if self.empty():
            return 0
        return np.average(self._brush_sizes)

    def addStrokePoint(self, position, brush_size):
        self._points.append(position)
        self._brush_sizes.append(brush_size)

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {"points": np.array(self._points).tolist(), "brush_sizes": self._brush_sizes}
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._points = data["points"]
        self._brush_sizes = data["brush_sizes"]


class StrokeSet(Data):
    ## Constructor
    def __init__(self, name="", color=(1.0, 0.0, 0.0, 0.4), with_empty=False):
        super(StrokeSet, self).__init__()
        self._strokes = []
        if with_empty:
            self.addEmptyStroke()
        self._color = color
        self._name = name

    def empty(self):
        return len(self._strokes) == 0

    def clear(self, with_empty=False):
        self._strokes = []
        if with_empty:
            self.addEmptyStroke()

    def name(self):
        return self._name

    def color(self):
        return self._color

    def strokes(self):
        return self._strokes

    def lastStroke(self):
        return self._strokes[-1]

    def addStroke(self, stroke):
        self._strokes.append(stroke)

    def addEmptyStroke(self):
        stroke = Stroke()
        self.addStroke(stroke)

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {}
        data["strokes"] = [stroke._dataDict() for stroke in self._strokes]
        data["name"] = self._name
        data["color"] = self._color

        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._strokes = []
        strokes_data = data["strokes"]
        for stroke_data in strokes_data:
            stroke = Stroke()
            stroke._setDataDict(stroke_data)
            self.addStroke(stroke)

        self._name = data["name"]
        self._color = data["color"]


class StrokeSets(Data):
    ## Constructor
    def __init__(self):
        self._stroke_sets = []
        self._selected_set = None

    def clear(self):
        self._stroke_sets = []
        self._selected_set = None

    def strokeSets(self):
        return self._stroke_sets

    def selectedStrokeSet(self):
        return self._selected_set

    def selectStrokeSet(self, name):
        for stroke_set in self._stroke_sets:
            if stroke_set.name() == name:
                self._selected_set = stroke_set
                return True
        return False

    def addStrokeSet(self, name, color):
        stroke_set = StrokeSet(name, color, with_empty=True)
        self._stroke_sets.append(stroke_set)
        self._selected_set = stroke_set

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {}
        data["stroke_sets"] = [stroke_set._dataDict() for stroke_set in self._stroke_sets]
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._stroke_sets = []
        stroke_sets_data = data["stroke_sets"]
        for stroke_set_data in stroke_sets_data:
            stroke_set = StrokeSet()
            stroke_set._setDataDict(stroke_set_data)
            self._stroke_sets.append(stroke_set)