
# -*- coding: utf-8 -*-
## @package ivf.scene.scene
#
#  ivf.scene.scene utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *


## Scene
class Scene(QObject):
    updatedImage = pyqtSignal(object)
    updatedMessage = pyqtSignal(str)

    ## Constructor
    def __init__(self):
        super(Scene, self).__init__()

        self._image = None
        self._layers = []
        self._selection = None

    def setImage(self, image):
        self._image = image
        self.updatedImage.emit(image)

    def image(self):
        return self._image

    def setLayers(self, layers):
        self._layers = layers

    def layers(self):
        return self._layers

    def setSelection(self, selection):
        self._selection = selection

    def Selection(self):
        return self._selection

    def setMessage(self, message):
        self.updatedMessage.emit(message)

