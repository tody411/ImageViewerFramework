
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
from ivf.cv.normal import normalToColor
from ivf.cv.image import alpha, gray2rgb, setAlpha, to8U


## Scene
class Scene(QObject, Data):
    updatedImage = pyqtSignal(object)
    updatedMessage = pyqtSignal(str)

    DisplayImage = 0
    DisplayNormal = 1
    DisplayDepth = 2

    ## Constructor
    def __init__(self):
        super(Scene, self).__init__()

        self._image = None
        self._image_file = ""
        self._normal = None
        self._depth = None
        self._layer_set = LayerSet()
        self._stroke_sets = StrokeSets()
        self._selection = None
        self._display_mode = self.DisplayImage

    def setDisplayMode(self, mode):
        if self._image is None:
            return

        self._display_mode = mode

        if self._display_mode == self.DisplayImage:
            self.updatedImage.emit(self._image)

        if self._display_mode == self.DisplayNormal:
            if self._normal is None:
                return
            normal_image = self.normalColor()
            self.updatedImage.emit(normal_image)

        if self._display_mode == self.DisplayDepth:
            if self._depth is None:
                return
            depth_image = self.depthImage()
            self.updatedImage.emit(depth_image)

    def displayMode(self):
        return self._display_mode

    def setImageFile(self, image_file):
        self._image_file = image_file
        image = loadRGBA(self._image_file)
        self.setImage(image)
        self._normal = None
        self._depth = None

    def setImage(self, image):
        self._image = image
        self.updatedImage.emit(image)

    def image(self):
        return self._image

    def setNormal(self, normal):
        self._normal = normal

    def normal(self):
        return self._normal

    def normalColor(self):
        A_8U = alpha(self._image)
        return normalToColor(self._normal, A_8U)

    def setDepth(self, depth):
        self._depth = depth

    def depth(self):
        return self._depth

    def depthImage(self):
        D_8U = to8U(self._depth)
        D_8U = gray2rgb(D_8U)
        A_8U = alpha(self._image)
        D_8U = setAlpha(D_8U, A_8U)
        return D_8U

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
