
# -*- coding: utf-8 -*-
## @package npr_sfs.ui.editor.file_selector
#
#  npr_sfs.ui.editor.file_selector utility package.
#  @author      tody
#  @date        2015/10/17


import os

from PyQt4.QtGui import *
from PyQt4.QtCore import *


## File selector with QFileSystemModel.
class FileListView(QListView):
    fileSelected = pyqtSignal(object)

    ## Constructor
    def __init__(self):
        super(FileListView, self).__init__()

        self.setMouseTracking(True)

        self._model = QFileSystemModel()

        self.open_events = []

        self.setModel(self._model)

        self.setUniformItemSizes(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.selectionModel().selectionChanged.connect(self.selectFile)
        self.update()

    def mouseDoubleClickEvent(self, event):
        for open_event in self.open_events:
            open_event(self.selectedFiles[0])

    def setRootPath(self, dir_path):
        self._model.setRootPath(dir_path)
        self.setRootIndex(self._model.index(dir_path))
        self.update()

    def setFilter(self, filter):
        self._model.setFilter(filter)

    def setNameFilters(self, filters):
        self._model.setNameFilters(filters)

    @property
    def selectedFiles(self):
        selectionModel = self.selectionModel()
        selectionModel.selectedIndexes()

        files = []
        for selectionIndex in selectionModel.selectedIndexes():
            file_path = str(self._model.filePath(selectionIndex))
            files.append(file_path)
        return files

    def selectFile(self):
        files = self.selectedFiles
        self.fileSelected.emit(files)

    def __repr__(self):
        return "FileListView: %s" %(self._model.rootPath())


class DirectoryListView(FileListView):

    ## Constructor
    def __init__(self):
        super(DirectoryListView, self).__init__()
        self._model.setFilter(QDir.NoDotAndDotDot | QDir.Dirs)


class DirectoryTreeView(QTreeView):
    fileSelected = pyqtSignal(object)

    ## Constructor
    def __init__(self):
        super(DirectoryTreeView, self).__init__()
        self.setMouseTracking(True)

        self._model = QFileSystemModel()
        self.setModel(self._model)
        self._model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)

        self.selectionModel().selectionChanged.connect(self.selectFile)

        self.setHeaderHidden(True)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.update()

    def setRootPath(self, dir_path):
        self._model.setRootPath(dir_path)
        self.setRootIndex(self._model.index(dir_path))
        self.update()

    def setFilter(self, filter):
        self._model.setFilter(filter)

    def setNameFilters(self, filters):
        self._model.setNameFilters(filters)

    @property
    def selectedFiles(self):
        selectionModel = self.selectionModel()
        selectionModel.selectedIndexes()

        files = []
        for selectionIndex in selectionModel.selectedIndexes():
            file_path = str(self._model.filePath(selectionIndex))
            files.append(file_path)
        return files

    def selectFile(self):
        files = self.selectedFiles
        self.fileSelected.emit(files)

    def __repr__(self):
        return "DirectoryTreeView: %s" % (self._model.rootPath())

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    selector = DirectoryTreeView()
    selector.show()

    print selector.setRootPath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    end = app.exec_()