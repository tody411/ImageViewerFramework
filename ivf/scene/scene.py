
# -*- coding: utf-8 -*-
## @package ivf.scene.scene
#
#  ivf.scene.scene utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.io_util.image import loadRGBA
from ivf.scene.data import Data
from ivf.scene.stroke import StrokeSets
from ivf.scene.layer import LayerSet


## Scene
class Scene(QObject, Data):
    updatedImage = pyqtSignal(object)
    updatedMessage = pyqtSignal(str)

    ## Constructor
    def __init__(self):
        super(Scene, self).__init__()

        self._image = None
        self._image_file = ""
        self._layer_set = LayerSet()
        self._stroke_sets = StrokeSets()
        self._selection = None

    def setImageFile(self, image_file):
        self._image_file = image_file
        image = loadRGBA(self._image_file)
        self.setImage(image)

    def setImage(self, image):
        self._image = image
        self.updatedImage.emit(image)

    def image(self):
        return self._image

    def strokeSets(self):
        return self._stroke_sets

    def layerSet(self):
        return self._layer_set

    def setSelection(self, selection):
        self._selection = selection

    def Selection(self):
        return self._selection

    def setMessage(self, message):
        self.updatedMessage.emit(message)

    ## dictionary data for writeJson method.
    def _dataDict(self):
        data = {"image_file": self._image_file}
        data["stroke"] = self._stroke_sets._dataDict()
        return data

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        self.setImageFile(data["image_file"])
        self._stroke_sets._setDataDict(data["stroke"])
