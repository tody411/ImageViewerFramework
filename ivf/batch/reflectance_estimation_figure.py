# -*- coding: utf-8 -*-
## @package ivf.batch.reflectance_estimation_figure
#
#  ivf.batch.reflectance_estimation_figure utility package.
#  @author      tody
#  @date        2016/02/21
import numpy as np
from scipy.spatial.distance import pdist
import cv2

import matplotlib.pyplot as plt

from ivf.datasets.colormap import colorMapFiles, loadColorMap
from ivf.core.sfs.reflectance_estimation import LambertReflectanceEstimation
from ivf.core.shader.light_sphere import normalSphere
from ivf.np.norm import normalizeVector, normVectors
from ivf.core.shader.toon import ColorMapShader
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.datasets.shape import shapeResultFile
from ivf.cv.image import luminance, setAlpha, to8U



def computeHistogram(M):
    M_8U = to8U(M.reshape(1, -1, 3))
    hist = cv2.calcHist([M_8U], [0, 1, 2], None, [32, 32, 32],
        [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist).flatten()

    return hist.flatten()

def compareHist(M1, M2):
    hist1 = computeHistogram(M1)
    hist2 = computeHistogram(M2)

    #return pdist(hist2 - hist1, 'cityblock')
    return cv2.compareHist(hist1, hist2, cv2.cv.CV_COMP_INTERSECT)

def computeGradientDistance(M1, M2):
    gM1 = M1[1:, :] - M1[:-1, :]
    gM2 = M2[1:, :] - M2[:-1, :]

    return np.linalg.norm(gM2 - gM1)

def errorTable():
    colormap_files = colorMapFiles()
    num_colormap_files = len(colormap_files)
    M_errors = np.zeros((num_colormap_files))

    for mi, colormap_file in enumerate(colormap_files):
        M_32F = loadColorMap(colormap_file)
        C_32F = M_32F.reshape(1, len(M_32F), 3)

        I_32F = np.linspace(0.0, 1.0, len(M_32F))
        I_32F = I_32F.reshape(C_32F.shape[:2])
        reflectance = LambertReflectanceEstimation(C_32F, I_32F)
        Ml = reflectance.shading(I_32F)[0, :, :]

        I0_32F = luminance(C_32F)
        IL_32F = luminance(Ml.reshape(1, -1, 3))

        I_min, I_max = np.min(I0_32F), np.max(I0_32F)

        M_error = normVectors(M_32F - Ml)

        #M_errors[mi] = np.mean(M_error) / (I_max - I_min)

        # M_errors[mi] = computeGradientDistance(M_32F, Ml) / (I_max - I_min)

        #M_errors[mi] = np.linalg.norm(I0_32F - IL_32F) / (I_max - I_min)

        M_errors[mi] = np.mean(M_error) / (I_max - I_min)

        # M_errors[mi] = np.linalg.norm(M_32F - Ml) / (I_max - I_min)
        # M_errors[mi] = compareHist(M_32F, Ml)

    file_path = shapeResultFile("ReflectanceEstimation", "ReflectanceError", file_ext=".npy")
    np.save(file_path, M_errors)

    plt.plot(M_errors)
    plt.show()
    # np.argsort(M_errors)


def loadReflectanceErrorTable():
    file_path = shapeResultFile("ReflectanceEstimation", "ReflectanceError", file_ext=".npy")
    return np.load(file_path)


def reflectanceErrorOrders():
    M_errors = loadReflectanceErrorTable()
    M_error_orders = np.argsort(M_errors)
    return M_error_orders


def colorMapFilesSortedReflectanceError():
    M_error_orders = reflectanceErrorOrders()
    colormap_files = colorMapFiles()
    colormap_files = [colormap_files[M_error_order] for M_error_order in M_error_orders]

    return colormap_files

def reflectanceEstimationFigure():
    errorTable()
    M_errors = loadReflectanceErrorTable()
    M_error_orders = np.argsort(M_errors)

    print M_errors[M_error_orders]

    colormap_files = colorMapFiles()
    colormap_files = [colormap_files[M_error_order] for M_error_order in M_error_orders]

    colormap_files = colormap_files[0:-1:3]

    Ms = []
    MLs = []
    for colormap_file in colormap_files:
        M_32F = loadColorMap(colormap_file)
        Ms.append(M_32F)

        C_32F = M_32F.reshape(1, len(M_32F), 3)
        I_32F = np.linspace(0.0, 1.0, len(M_32F))
        I_32F = I_32F.reshape(C_32F.shape[:2])
        reflectance = LambertReflectanceEstimation(C_32F, I_32F)
        Ml = reflectance.shading(I_32F)

        MLs.append(Ml[0, :, :])

    num_rows = 3
    num_cols = len(colormap_files)

    w = 10
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, hspace=0.05, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    N_sphere, A_32F = normalSphere(h=512, w=512)
    Lg = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    plot_grid = SubplotGrid(num_rows, num_cols)

    mi = 1

    for M, Ml in zip(Ms, MLs):
        CM_32F = ColorMapShader(M).diffuseShading(Lg, N_sphere)
        CL_32F = ColorMapShader(Ml).diffuseShading(Lg, N_sphere)
        C_error = normVectors((CM_32F - CL_32F).reshape(-1, 3)).reshape(CL_32F.shape[:2])
        C_error[A_32F < 0.5 * np.max(A_32F)] = 0.0

        plot_grid.setPlot(1, mi)
        plot_grid.showImage(setAlpha(CM_32F, A_32F), "")
        plot_grid.setPlot(2, mi)
        plot_grid.showImage(setAlpha(CL_32F, A_32F), "")
        plot_grid.setPlot(3, mi)
        plot_grid.showColorMap(C_error, "", v_min=0.0, v_max=0.3, with_colorbar=False)

        mi += 1

    file_path = shapeResultFile("ReflectanceEstimation", "ReflectanceEstimationError")
    fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    reflectanceEstimationFigure()
