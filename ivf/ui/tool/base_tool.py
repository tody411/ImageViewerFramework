
# -*- coding: utf-8 -*-
## @package inversetoon.pyqt.tool.base_tool
#
#  inversetoon.pyqt.tool.base_tool utility package.
#  @author      tody
#  @date        2015/07/21

from PyQt4.QtGui import *
from PyQt4.QtCore import *


## Base Tool.
class BaseTool(QObject):
    ## Constructor
    def __init__(self):
        super(BaseTool, self).__init__()

    def setView(self, view):
        self._view = view
        self._view.setOverlayFunc(self._overlayFunc)

    def mousePressEvent(self, e):
        print "mousePressEvent:", self._mousePosition(e)

    def mouseReleaseEvent(self, e):
        print "mouseReleaseEvent:", self._mousePosition(e)

    def mouseMoveEvent(self, e):
        print "mouseMoveEvent:", self._mousePosition(e)

    def wheelEvent(self, e):
        pass

    def keyPressEvent(self, e):
        print "keyPressEvent:", str(e.key())

    def keyReleaseEvent(self, e):
        print "keyReleaseEvent:", str(e.key())

    def _mousePosition(self, e):
        p = self._view._numpy_position(e)
        return self._view.unproject(p)

    def _overlayFunc(self, painter):
        pass
