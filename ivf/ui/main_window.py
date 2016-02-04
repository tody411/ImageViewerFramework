
# -*- coding: utf-8 -*-
## @package ivf.ui.main_window
#
#  ivf.ui.main_window utility package.
#  @author      tody
#  @date        2016/01/25


from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.ui.image_view import ImageView
from ivf.scene.scene import Scene
from ivf.cmds.image import LoadImageCommand, SaveImageCommand
from ivf.cmds.quit import QuitCommand
from ivf.cmds.stroke_tool import StrokeToolCommand
from ivf.cmds.scene import LoadSceneCommand, SaveSceneCommand
from ivf.cmds.resize import ResizeImageCommand
from ivf.cmds.graph_cut import GraphCutCommand
from ivf.cmds.overlay.scene_info import SceneInfoOverlayCommand
from ivf.cmds.overlay.layer import LayerOverlayCommand
from ivf.cmds.slic import SlicCommand
from ivf.cmds.display.display_cmd import DisplayCommand
from ivf.cmds.sfs.ibme import IBMECommand
from ivf.cmds.sfs.lumo import LumoCommand
from ivf.cmds.sfs.depth_from_normal import DepthFromNormalCommand
from ivf.cmds.window.depth_view import DepthViewCommand
from ivf.ui.glview import GLView
from ivf.cmds.load_normal import LoadNormalCommand
from ivf.cmds.save_depth import SaveDepthCommand
from ivf.cmds.sparse_interpolation.bilateral_smoothing import BilateralSmoothingCommand
from ivf.cmds.sparse_interpolation.bilateral_normal_smoothing import BilateralNormalSmoothingCommand
from ivf.cmds.sparse_interpolation.sparse_sampling import SparseSamplingCommand
from ivf.cmds.sfs.depth_to_normal import DepthToNormalCommand
from ivf.ui.model_view import ModelView


## Main Window
class MainWindow(QMainWindow):

    ## Constructor
    def __init__(self, dataset_browser=None):
        super(MainWindow, self).__init__()
        self.setAcceptDrops(True)
        self._scene = Scene()
        self._image_view = ImageView()
        self._depth_view = ModelView()

        self._createCentralWidget([('Image View', self._image_view),
                                   ('Depth View', self._depth_view)])

        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)
        self.showMaximized()

        self._createMenus()

        self._scene.updatedImage.connect(self._image_view.render)
        self._scene.updatedDepth.connect(self._depth_view.setRGBAD)
        self._scene.updatedMessage.connect(self._status_bar.showMessage)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle("Image Viewer")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            scene_file = str(url.toLocalFile())
            cmd = LoadImageCommand(self._scene, scene_file)
            cmd.run()

    def closeEvent(self, event):
        QApplication.closeAllWindows()

    def _createMenus(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")
        self._addCommand(LoadSceneCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(SaveSceneCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(LoadImageCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(SaveImageCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(LoadNormalCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(SaveDepthCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(QuitCommand(self._scene, parent=file_menu), file_menu)

        operation_menu = menu_bar.addMenu("&Image Operation")
        self._addCommand(ResizeImageCommand(self._scene, (0.5, 0.5), "&Down scale", parent=operation_menu), operation_menu)
        self._addCommand(SlicCommand(self._scene, parent=operation_menu), operation_menu)
        self._addCommand(BilateralSmoothingCommand(self._scene, parent=operation_menu), operation_menu)
        self._addCommand(SparseSamplingCommand(self._scene, parent=operation_menu), operation_menu)

        sfs_menu = menu_bar.addMenu("&Shape From Shading")
        self._addCommand(IBMECommand(self._scene, parent=sfs_menu), sfs_menu)
        self._addCommand(LumoCommand(self._scene, parent=sfs_menu), sfs_menu)
        self._addCommand(DepthFromNormalCommand(self._scene, parent=sfs_menu), sfs_menu)
        self._addCommand(DepthToNormalCommand(self._scene, parent=sfs_menu), sfs_menu)
        self._addCommand(BilateralNormalSmoothingCommand(self._scene, parent=sfs_menu), sfs_menu)

        tool_menu = menu_bar.addMenu("&Tool")
        self._addCommand(GraphCutCommand(self._scene, self._image_view, parent=tool_menu), tool_menu)
        self._addCommand(StrokeToolCommand(self._scene, self._image_view, parent=tool_menu), tool_menu)

        overlay_menu = menu_bar.addMenu("&Overlay")
        self._addCommand(SceneInfoOverlayCommand(self._scene, self._image_view, parent=overlay_menu), overlay_menu)
        self._addCommand(LayerOverlayCommand(self._scene, self._image_view, parent=overlay_menu), overlay_menu)

        display_menu = menu_bar.addMenu("&Display")
        display_command_action_group = DisplayCommand(self._scene, self._image_view, parent=display_menu).actionGroup()
        for action in display_command_action_group.actions():
            display_menu.addAction(action)

    def _addCommand(self, cmd, parent_menu):
        parent_menu.addAction(cmd.action())

    def _createCentralWidget(self, widgets):
        tab_widget = QTabWidget()

        for name, widget in widgets:
            tab_widget.addTab(widget, name)

        tab_widget.setCurrentIndex(0)
        self.setCentralWidget(tab_widget)


def runGUI():
    import sys
    app = QApplication(sys.argv)

    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    runGUI()