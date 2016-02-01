
# -*- coding: utf-8 -*-
## @package ivf.core.sfs.silhouette_normal
#
#  ivf.core.sfs.silhouette_normal utility package.
#  @author      tody
#  @date        2016/02/01


import numpy as np
import cv2


## Silhouette normal from the alpha mask.
def silhouetteNormal(A_8U, sigma=7.0):
    height, width = A_8U.shape[0], A_8U.shape[1]

    A_8U_blur = cv2.GaussianBlur(A_8U, (0, 0), width * sigma / 1024.0)
    A_8U_blur = (1.0 / 255.0) * np.float32(A_8U_blur)

    gx = cv2.Sobel(A_8U_blur, cv2.CV_64F, 1, 0, ksize=5)
    gy = cv2.Sobel(A_8U_blur, cv2.CV_64F, 0, 1, ksize=5)

    N_32F = np.zeros((height, width, 3), dtype=np.float32)

    N_32F[:, :, 0] = -gx
    N_32F[:, :, 1] = gy
    N_32F[:, :, 2] = A_8U_blur

    gxy_norm = np.zeros((height, width))

    gxy_norm[:, :] = np.sqrt(gx[:, :] * gx[:, :] + gy[:, :] * gy[:, :])

    Nxy_norm = np.zeros((height, width))
    Nxy_norm[:, :] = np.sqrt(1.0 - A_8U_blur[:, :])

    wgxy = np.zeros((height, width))
    wgxy[:, :] = Nxy_norm[:, :] / (0.001 + gxy_norm[:, :])

    N_32F[:, :, 0] = wgxy[:, :] * N_32F[:, :, 0]
    N_32F[:, :, 1] = wgxy[:, :] * N_32F[:, :, 1]

    return N_32F
