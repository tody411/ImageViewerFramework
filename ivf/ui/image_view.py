
# -*- coding: utf-8 -*-
## @package ivf.ui.image_view
#
#  ivf.ui.image_view utility package.
#  @author      tody
#  @date        2016/01/25

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import numpy as np

from ivf.ui.tool.camera_tool import CameraTool2D
from ivf.ui.tool.stroke_tool import StrokeTool
from ivf.ui.qimage_util import ndarrayToQImage
from ivf.ui.tool.normal_constraint_tool import NormalConstraintTool


## Image View
class ImageView(QWidget):
    ## Constructor
    def __init__(self):
        super(ImageView, self).__init__()
        self._q_image = None
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self._tool = None
        self._cameraTool = CameraTool2D()
        self._transform = QTransform()
        self._dafault_transform = QTransform()
        self._center_to_view_transform = QTransform()
        self._cameraTool.outTransform.connect(self.setTransform)

        self._overlay_func = None
        self._scene_overlays = []
        self._view_overlays = []
        self._image_overlyas = []

        self.setWindowTitle("Image View")

        self._return_func = None
        self._image = None

    def setReturnCallback(self, return_func):
        self._return_func = return_func

    def setTransform(self, transform):
        self._transform = transform
        self.update()

    def render(self, image):
        self._image = image
        self._q_image = ndarrayToQImage(image)

        self.update()

    def image(self):
        return self._image

    def setOverlayFunc(self, overlay_func):
        self._overlay_func = overlay_func

    def addSceneOverlay(self, overlay):
        self._scene_overlays.append(overlay)

    def addViewOverlay(self, overlay):
        self._view_overlays.append(overlay)

    def addImageOverlay(self, overlay):
        self._image_overlyas.append(overlay)

    def transform(self):
        if self._q_image is None:
            return QTransform()

        scale = self._defaultScale()
        image_center = self._imageCenter()
        tocenter_transform = QTransform().translate(-image_center[0], -image_center[1])

        world_trasform = tocenter_transform * QTransform().scale(scale, scale) * self._transform

        view_center = self._viewCenter()
        center_to_view_transform = QTransform()
        center_to_view_transform.translate(view_center[0], view_center[1])
        return world_trasform * center_to_view_transform

    def project(self, p):
        px, py = self.transform().map(p[0], p[1])
        return np.array([px, py])

    def unproject(self, p):
        px, py = self.transform().inverted()[0].map(p[0], p[1])
        return np.array([px, py])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient (0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor.fromRgbF(0.5, 0.6, 0.7))
        gradient.setColorAt(1.0, QColor.fromRgbF(0.1, 0.1, 0.1))

        painter.setBrush(gradient)
        painter.drawRect(0, 0, self.width(), self.height())

        painter.setWorldTransform(self.transform())

        if self._q_image is None:
            return

        painter.drawImage(0, 0, self._q_image)

        for overlay in self._image_overlyas:
            q_image = overlay()
            if q_image is not None:
                painter.drawImage(0, 0, q_image)

        if self._overlay_func:
            self._overlay_func(painter)

        for overlay in self._scene_overlays:
            overlay(painter)

        painter.setWorldTransform(QTransform())
        for overlay in self._view_overlays:
            overlay(painter)

    def setTool(self, tool):
        self._tool = tool
        self._tool.setView(self)

    def setCameraTool(self, cameraTool):
        self._cameraTool = cameraTool
        self._cameraTool.setView(self)

    def mousePressEvent(self, e):
        self._cameraTool.mousePressEvent(e)

        if self._tool is not None:
            self._tool.mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self._cameraTool.mouseReleaseEvent(e)
        if self._tool is not None:
            self._tool.mouseReleaseEvent(e)

    def mouseMoveEvent(self, e):
        self._cameraTool.mouseMoveEvent(e)
        if self._tool is not None:
            self._tool.mouseMoveEvent(e)

    def wheelEvent(self, e):
        self._cameraTool.wheelEvent(e)
        if self._tool is not None:
            self._tool.wheelEvent(e)

    def keyPressEvent(self, e):
        self._cameraTool.keyPressEvent(e)
        if self._tool is not None:
            self._tool.keyPressEvent(e)

        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            if self._return_func is not None:
                self._return_func()

    def keyReleaseEvent(self, e):
        self._cameraTool.keyReleaseEvent(e)
        if self._tool is not None:
            self._tool.keyReleaseEvent(e)

    def resizeEvent(self, e):
        self.update()

    def _viewCenter(self):
        viewport = self.size()
        viewport = np.array([viewport.width(), viewport.height()], dtype=np.float32)
        return 0.5 * viewport

    def _imageCenter(self):
        image_size = self._q_image.size()
        image_size = np.array([image_size.width(), image_size.height()], dtype=np.float32)
        return 0.5 * image_size

    def _defaultScale(self):
        if self._q_image is None:
            return 1.0

        viewport = self.size()
        viewport = np.array([viewport.width(), viewport.height()], dtype=np.float32)
        image_size = self._q_image.size()
        image_size = np.array([image_size.width(), image_size.height()], dtype=np.float32)

        scale = viewport / image_size
        scale = min(scale[0], scale[1])
        return scale

    def _qpoint_to_numpy(self, qp):
        return np.array([qp.x(), qp.y()])

    def _numpy_position(self, e):
        pos = e.pos()
        return self._qpoint_to_numpy(pos)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    view = ImageView()
    view.show()
    tool = NormalConstraintTool()
    view.setTool(tool)

    image = np.random.rand(256, 256, 3)
    view.render(image)

    end = app.exec_()
