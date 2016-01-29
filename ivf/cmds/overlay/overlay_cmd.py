
# -*- coding: utf-8 -*-
## @package ivf.cmds.overlay.overlay_cmd
#
#  ivf.cmds.overlay.overlay_cmd utility package.
#  @author      tody
#  @date        2016/01/27


from PyQt4.QtGui import *
from PyQt4.QtCore import *


class OverlayCommand(QObject):
    def __init__(self, scene, view, name="", parent=None):
        super(OverlayCommand, self).__init__()
        self._name = name
        self._scene = scene
        self._view = view
        self._view.addSceneOverlay(self._sceneOverlay)
        self._view.addViewOverlay(self._viewOverlay)
        self._show_sceneOverlay = False
        self._action = None
        self._parent = parent

    def name(self):
        return self._name

    def action(self):
        if self._action is not None:
            return self._action

        def toggleFunc(checked):
            self._show_sceneOverlay = checked
            self._imageOverlay()
            self._view.update()

        self._action = QAction(self._name, self._parent)
        self._action.setCheckable(True)
        self._action.toggled.connect(toggleFunc)
        return self._action

    def _sceneOverlay(self, painter):
        if self._show_sceneOverlay:
            self._sceneOverlayImp(painter)

    def _viewOverlay(self, painter):
        if self._show_sceneOverlay:
            self._viewOverlayImp(painter)

    def _imageOverlay(self):
        if self._show_sceneOverlay:
            image = self._scene.image()
            image = self._imageOverlayImp(image)
            self._view.render(image)

    def _sceneOverlayImp(self, painter):
        pass

    def _viewOverlayImp(self, painter):
        pass

    def _imageOverlayImp(self, image):
        return image
