
# -*- coding: utf-8 -*-
## @package npr_sfs.ui.editor.list_edit
#
#  npr_sfs.ui.editor.list_edit utility package.
#  @author      tody
#  @date        2015/10/27

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class ListModel(QStringListModel):
    ## Constructor
    def __init__(self, parent=None):
        super(ListModel, self).__init__(parent)

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled

        return Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled


## List Edit
class ListEdit(QWidget):

    valueSelected = pyqtSignal(object)

    ## Constructor
    def __init__(self, values=[]):
        super(ListEdit, self).__init__()

        list_view = QListView()
        self._model = ListModel()
        list_view.setModel(self._model)
        list_view.setMovement(QListView.Snap)
        list_view.setDragDropMode(QListView.InternalMove)
        list_view.setDragDropOverwriteMode(False)
        list_view.setDropIndicatorShown(True)

        self.setValues(values)

        self._newItemEdit = QLineEdit()

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.addItem)

        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.deleteItem)

        layout = QGridLayout()
        layout.addWidget(self._newItemEdit, 0, 0)
        layout.addWidget(add_button, 0, 1)
        layout.addWidget(list_view, 1, 0)
        layout.addWidget(delete_button, 1, 1)
        self.setLayout(layout)

        self._selectionModel = list_view.selectionModel()
        self._selectionModel.selectionChanged.connect(self.selectValue)
        self._newItemEdit.returnPressed.connect(self.addItem)
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.deleteItem()

    def addItem(self):
        dataList = self._model.stringList()
        dataList << str(self._newItemEdit.text())
        self._model.setStringList(dataList)
        self.update()

    def deleteItem(self):
        dataList = self._model.stringList()
        value = self.selectedValue

        if value != "":
            dataList.removeAll(value)
            self._model.setStringList(dataList)
            self.update()

    def setValues(self, values):
        dataList = QStringList()
        dataList << values
        self._model.setStringList(dataList)
        self.update()

    def getValues(self):
        dataList = self._model.stringList()
        dataList = [str(data) for data in dataList]
        return dataList

    @property
    def selectedValue(self):
        selectionModel = self._selectionModel
        selectionModel.selectedIndexes()

        for selectionIndex in selectionModel.selectedIndexes():
            valueStr = str(self._model.data(selectionIndex, Qt.DisplayRole).toString())
            return valueStr
        return ""

    def selectValue(self):
        selectionModel = self._selectionModel
        selectionModel.selectedIndexes()

        for selectionIndex in selectionModel.selectedIndexes():
            valueStr = str(self._model.data(selectionIndex, Qt.DisplayRole).toString())
            self.valueSelected.emit(valueStr)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    edit = ListEdit(["v1", "v2"])
    edit.show()
    print edit.getValues()
    end = app.exec_()