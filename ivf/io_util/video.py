# -*- coding: utf-8 -*-
## @package ivf.io_util.video
#
#  ivf.io_util.video utility package.
#  @author      tody
#  @date        2016/02/17


import cv2
from ivf.util.timer import timing_func
from ivf.cv.image import bgr2rgb, rgb2bgr, rgb, to8U


@timing_func
def loadVideo(file_path):
    loader = cv2.VideoCapture(file_path)

    images = []

    while(loader.isOpened()):
        ret, frame = loader.read()

        if ret == False:
            break

        frame_rgb = bgr2rgb(frame)

        images.append(frame_rgb)

    loader.release()
    return images


@timing_func
def saveVideo(file_path, images, fps=30, size=None):
    if size is None:
        h, w = images[0].shape[:2]
        size = (w, h)

        print size

    fourcc = cv2.cv.CV_FOURCC('W', 'M', 'V', '2')
    writer = cv2.VideoWriter(file_path, fourcc, fps, size, True)

    for image in images:
        bgr = rgb2bgr(to8U(rgb(image)))
        writer.write(bgr)

    writer.release()
