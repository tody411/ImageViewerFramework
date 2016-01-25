
# PyQt modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

_attrLabelPreferredWidth = 80

class AttributeLabel(QLabel):
    def __init__(self, name = ""):
        super(AttributeLabel, self).__init__("&%s:" %name)
        self.setMaximumWidth(_attrLabelPreferredWidth)
        self.setMinimumWidth(_attrLabelPreferredWidth)

# Numeric slider group.
class NumericSliderGroup(QWidget):
    valueChanged = pyqtSignal(float)

    ui_maximumHeight = 50
    valueEditMaximumWidth = 100
    epsilon = 1e-6

    ## Constructor
    def __init__(self, name = "", minVal = 0, maxVal = 100, defaultVal = 0, dataType = int):
        super(NumericSliderGroup, self).__init__()

        self._name = name
        self._minVal = minVal
        self._maxVal = maxVal
        self._dataType = dataType
        self.createUI()
        self.setValue(defaultVal, False)
        self.setWindowTitle(name)
        self.setMaximumHeight(self.ui_maximumHeight)

    def createUI(self):
        nameLabel = AttributeLabel(self._name)
        self._valueEdit = QLineEdit()
        self._valueEdit.editingFinished.connect( self.valueEditChanged )
        self._valueEdit.setMaximumWidth(self.valueEditMaximumWidth)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setFocusPolicy(Qt.StrongFocus)
        self._slider.setSingleStep(1)
        self._slider.sliderMoved.connect(self.sliderChanged)

        self.setMinMax(self._minVal, self._maxVal)

        nameLabel.setBuddy(self._valueEdit)

        layout = QGridLayout()
        layout.addWidget(nameLabel, 0, 0)
        layout.addWidget(self._valueEdit, 0, 1)
        layout.addWidget(self._slider, 0, 2)
        self.setLayout(layout)

    def setMinMax(self, minVal = 0, maxVal = 100):
        self._minVal = minVal
        self._maxVal = maxVal
        self._setSliderMinMax(minVal, maxVal)
        self._setValidator(minVal, maxVal)

    def setValue(self, val, isEmit = True):
        isModified = self._isModified(val)

        self._setSliderValue(val)
        self._setValueEditValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    @property
    def value(self):
        return self._sliderValue()

    def sliderChanged(self, val, isEmit = True):
        isModified = self._isModified(val)

        val = self._sliderValue()
        self._setValueEditValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    def valueEditChanged(self, isEmit = True):
        val = self._valueEditValue()
        isModified = self._isModified(val)

        self._setSliderValue(val)
        if isEmit and isModified:
            self.valueChanged.emit(val)

    def _sliderValue(self):
        return self._slider.value()

    def _valueEditValue(self):
        return self._dataType ( self._valueEdit.text() )

    def _isModified(self, val):
        val_old = self.value
        return abs( val - val_old) > self.epsilon

    def _setSliderMinMax(self, minVal, maxVal):
        self._slider.setMinimum(self._minVal)
        self._slider.setMaximum(self._maxVal)

    def _setValidator(self, minVal, maxVal):
        self._valueEdit.setValidator(QIntValidator(self._minVal, self._maxVal, self._valueEdit))

    def _setSliderValue(self, val):
        self._slider.setValue( val )

    def _setValueEditValue(self, val):
        self._valueEdit.setText('%s' %val)


## Int slider group.
class IntSliderGroup(NumericSliderGroup):

    ## Constructor
    def __init__(self, name = "", minVal = 0, maxVal = 100, defaultVal = 0):
        super(IntSliderGroup, self).__init__(name, minVal, maxVal, defaultVal, int)

## Float slider group.
class FloatSliderGroup(NumericSliderGroup):
    sliderMaximum = 1000

    ## Constructor
    def __init__(self, name = "", minVal = 0.0, maxVal = 1.0, defaultVal = 0.0):
        super(FloatSliderGroup, self).__init__(name, minVal, maxVal, defaultVal, float)
        self._slider.setMinimum(0)
        self._slider.setMaximum(self.sliderMaximum)

    def _sliderValue(self):
        return self._minVal + (self._maxVal - self._minVal) * self._slider.value() / float( self.sliderMaximum)

    def _setSliderValue(self, val):
        t = (val - self._minVal) / ( self._maxVal - self._minVal )
        sliderVal = self.sliderMaximum * t
        self._slider.setValue(sliderVal)

    def _setSliderMinMax(self, minVal, maxVal):
        pass

    def _setValidator(self, minVal, maxVal):
        self._valueEdit.setValidator(QDoubleValidator(self._minVal, self._maxVal, 6, self._valueEdit))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    editor = QWidget()
    layout = QVBoxLayout()
    layout.addWidget(IntSliderGroup("IntSlider"))
    layout.addWidget(FloatSliderGroup("FloatSlider"))
    editor.setLayout(layout)
    editor.show()
    end = app.exec_()