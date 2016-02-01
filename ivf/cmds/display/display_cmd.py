
# -*- coding: utf-8 -*-
## @package ivf.cmds.display.display_cmd
#
#  ivf.cmds.display.display_cmd utility package.
#  @author      tody
#  @date        2016/02/01

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ivf.scene.scene import Scene


class DisplayCommand(QObject):
    def __init__(self, scene, view, name="", parent=None):
        super(DisplayCommand, self).__init__()
        self._name = name
        self._scene = scene
        self._view = view
        self._action_group = None
        self._parent = parent

        self._createActionGroup()

    def name(self):
        return self._name

    def actionGroup(self):
        if self._action_group is not None:
            return self._action_group

    def _createActionGroup(self):
        self._action_group = QActionGroup(self._parent)
        image_action = self._addDisplayAction("Display Image", Scene.DisplayImage)
        self._addDisplayAction("Display Normal", Scene.DisplayNormal)
        self._addDisplayAction("Display Depth", Scene.DisplayDepth)
        image_action.setChecked(True)

    def _addDisplayAction(self, name, mode):
        action = self._displayAction(name, mode)
        self._action_group.addAction(action)
        return action

    def _displayAction(self, name, mode):
        def toggleFunc(checked):
            self._scene.setDisplayMode(mode)
            self._view.update()
        action = QAction(name, self._parent)
        action.setCheckable(True)
        action.toggled.connect(toggleFunc)
        return action