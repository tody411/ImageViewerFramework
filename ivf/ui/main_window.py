
# -*- coding: utf-8 -*-
## @package ivf.ui.main_window
#
#  ivf.ui.main_window utility package.
#  @author      tody
#  @date        2016/01/25


from PyQt4.QtGui import *
from PyQt4.QtCore import *

from ivf.ui.image_view import ImageView
from ivf.io_util.image import loadRGBA
from ivf.scene.scene import Scene
from ivf.cmds.image import LoadImageCommand, SaveImageCommand
from ivf.cmds.quit import QuitCommand


## Main Window
class MainWindow(QMainWindow):

    ## Constructor
    def __init__(self, dataset_browser=None):
        super(MainWindow, self).__init__()
        self.setAcceptDrops(True)
        self._scene = Scene()
        self._image_view = ImageView()
        self.setCentralWidget(self._image_view)

        self._status_bar = QStatusBar(self)
        self.setStatusBar(self._status_bar)
        self.showMaximized()

        self._createMenus()

        self._scene.updatedImage.connect(self._image_view.render)
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
        self._addCommand(LoadImageCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(SaveImageCommand(self._scene, parent=file_menu), file_menu)
        self._addCommand(QuitCommand(self._scene, parent=file_menu), file_menu)

        edit_menu = menu_bar.addMenu("&Edit")


    def _addCommand(self, cmd, parent_menu):
        parent_menu.addAction(cmd.action())


def runGUI():
    import sys
    app = QApplication(sys.argv)

    win = MainWindow()
    win.showMaximized()
    sys.exit(app.exec_())

if __name__ == '__main__':
    runGUI()