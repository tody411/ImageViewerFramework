
# -*- coding: utf-8 -*-
## @package ivf.cmds.stroke_tool
#
#  ivf.cmds.stroke_tool utility package.
#  @author      tody
#  @date        2016/01/26


from ivf.cmds.base_cmds import BaseCommand
from ivf.ui.tool.stroke_tool import StrokeTool


class StrokeToolCommand(BaseCommand):
    def __init__(self, scene, view, parent=None):
        super(StrokeToolCommand, self).__init__(scene, "&Stroke Tool", parent)
        self._view = view
        self._tool = StrokeTool()
        action = self.action()
        action.setShortcut("S")

    def _runImp(self):
        self._view.setTool(self._tool)
