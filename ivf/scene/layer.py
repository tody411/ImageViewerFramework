# -*- coding: utf-8 -*-
## @package ivf.scene.layer
#
#  ivf.scene.layer utility package.
#  @author      tody
#  @date        2016/01/27

import numpy as np

from ivf.scene.data import Data


class Layer(Data):
    ## Constructor
    def __init__(self, name="", color=(1.0, 0.0, 0.0, 0.4), mask=None):
        super(Layer, self).__init__()
        self._mask = mask
        self._name = name
        self._color = color

    def name(self):
        return self._name

    def color(self):
        return self._color

    def mask(self):
        return self._mask

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {}
        data["name"] = self._name
        data["color"] = self._color

        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self._name = data["name"]
        self._color = data["color"]


class LayerSet(Data):
    ## Constructor
    def __init__(self):
        super(LayerSet, self).__init__()
        self._layers = []

    def layers(self):
        return self._layers

    def clear(self):
        self._layers = []

    def addLayer(self, layer):
        self._layers.append(layer)