# -*- coding: utf-8 -*-
## @package ivf.batch.shape_estimation_figure
#
#  ivf.batch.shape_estimation_figure utility package.
#  @author      tody
#  @date        2016/02/19
import numpy as np
import matplotlib.pyplot as plt
import cv2

from ivf.datasets.colormap import colorMapFile, loadColorMap, colorMapFiles
from ivf.plot.window import SubplotGrid, showMaximize
from ivf.np.norm import normalizeVector, normVectors
from ivf.core.shader.light_sphere import lightSphere
from ivf.core.sfs.colormap_sphere import colorMapSphere
from ivf.datasets.shape import shapeFile, shapeResultFile, shapeNames, shapeFiles
from ivf.io_util.image import loadNormal, loadRGBA
from ivf.core.sfs.pr_sfs import Wu08SFS
from ivf.core.shader.toon import ColorMapShader
from ivf.cv.normal import normalToColor
from ivf.core.shader.lambert import LambertShader
from ivf.cv.image import to32F, setAlpha, trim, gray2rgb, to8U
from ivf.core.sfs.toon_sfs import ToonSFS
from ivf.core.sfs.angle_error import angleErros
from ivf.core.shader.shader import LdotN
from ivf.core.sfs.colormap_estimation import ColorMapEstimation
from ivf.batch.reflectance_estimation_figure import colorMapFilesSortedReflectanceError, reflectanceErrorOrders


def computeLambertShadingError():
    shape_names = shapeNames()

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    C_errors = np.zeros(len(shape_names))
    N_errors = np.zeros(len(shape_names))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        C0_32F = LambertShader().diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.setNumIterations(iterations=60)
        sfs_method.run()
        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
        C_error = sfs_method.shadingError()
        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0

        C_errors[si] = np.average(C_error[A_8U > 0.5 * np.max(A_8U)])

        h, w = A_8U.shape[:2]
        N_error = angleErros(N_32F.reshape(-1, 3), Ng_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        N_errors[si] = np.average(N_error[A_8U > 0.5 * np.max(A_8U)])

    file_path = shapeResultFile("ShapeEstimation", "ShadingError", file_ext=".npy")
    np.save(file_path, C_errors)

    file_path = shapeResultFile("ShapeEstimation", "NormalError", file_ext=".npy")
    np.save(file_path, N_errors)


def errorInfo():
    shape_names = shapeNames()
    file_path = shapeResultFile("ShapeEstimation", "ShadingError", file_ext=".npy")
    C_errors = np.load(file_path)
    C_error_orders = np.argsort(C_errors)

    print "Small Shading Error: ", np.min(C_errors)
    for C_error_order in C_error_orders[:5]:
        print "  ", shape_names[C_error_order]

    print "Large Shading Error: ", np.max(C_errors)
    for C_error_order in C_error_orders[-5:]:
        print "  ", shape_names[C_error_order]

    file_path = shapeResultFile("ShapeEstimation", "NormalError", file_ext=".npy")
    N_errors = np.load(file_path)

    N_error_orders = np.argsort(N_errors)

    print "Small Normal Error: ", np.min(N_errors)
    for N_error_order in N_error_orders[:5]:
        print "  ", shape_names[N_error_order]

    print "Large Normal Error: ", np.max(N_errors)
    for N_error_order in N_error_orders[-5:]:
        print "  ", shape_names[N_error_order]


def LambertShadingFigure():
    target_shapes = ["Sphere", "Cone", "Blob1", "Man", "Cone", "OctaFlower", "Pulley", "Grog", "Lucy", "Raptor"]
    target_shapes = ["Blob1", "Pulley", "Lucy"]
    shape_names = target_shapes

    num_rows = len(shape_names)
    num_cols = 6

    w = 20
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.02, hspace=0.15, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.2, 0.3, 0.6]))

    for si, shape_name in enumerate(shape_names):
        Ng_data = shapeFile(shape_name)

        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data

        C0_32F = LambertShader().diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.setNumIterations(iterations=70)
        sfs_method.setWeights(w_lap=1.0)
        sfs_method.run()
        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
        C_error = sfs_method.shadingError()
        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        C_error = trim(C_error, A_8U)

        h, w = A_8U.shape
        N_error = angleErros(N_32F.reshape(-1, 3), Ng_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        N_error = trim(N_error, A_8U)

        title = ""
        if si == 0:
            title =  "Ground-truth"
        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), title)

        title = ""
        if si == 0:
            title =  "Our result"
        plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), title)

        title = ""
        if si == 0:
            title = "Error (shading)"
        plot_grid.showColorMap(C_error, title, v_min=0, v_max=0.1, with_colorbar=True)

        title = ""
        if si == 0:
            title =  "Ground-truth"
        plot_grid.showImage(normalToColor(Ng_32F, A_8U), title)

        title = ""
        if si == 0:
            title = "Our result"
        plot_grid.showImage(normalToColor(N_32F, A_8U), title)

        title = ""
        if si == 0:
            title = "Error (shape)"

        plot_grid.showColorMap(N_error, title, v_min=0, v_max=30.0, with_colorbar=True)

    file_path = shapeResultFile("ShapeEstimation", "LambertEstimationError", file_ext=".pdf")
    fig.savefig(file_path, transparent=True)


def materialShapeVariationFigure():
    target_colormaps = [23, 3, 12]
    #target_colormaps = [3, 17]
    colormap_files = [colorMapFile(cmap_id) for cmap_id in target_colormaps]

    target_shapes = ["Blob1", "ThreeBox"]
    shape_names = target_shapes
    #shape_names = shapeNames()[4:5]

    num_shapes = len(shape_names)
    num_colormaps = len(colormap_files)
    num_rows = num_colormaps
    num_cols = 6

    w = 20
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.02, hspace=0.15, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    shape_name = "Blob1"

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data

    for mi, colormap_file in enumerate(colormap_files):
        M_32F = loadColorMap(colormap_file)
        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        sfs_method = ToonSFS(L, C0_32F, A_8U)
        sfs_method.setInitialNormal(N0_32F)
        sfs_method.setNumIterations(iterations=40)
        sfs_method.setWeights(w_lap=5.0)
        sfs_method.run()

        N_32F = sfs_method.normal()
        C_32F = sfs_method.shading()
            #C_32F = cv2.bilateralFilter(C_32F, 0, 0.1, 3)
        C_error = sfs_method.shadingError()

        C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        C_error = trim(C_error, A_8U)

        h, w = A_8U.shape
        N_error = angleErros(N_32F.reshape(-1, 3), Ng_32F.reshape(-1, 3)).reshape(h, w)
        N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
        N_error = trim(N_error, A_8U)

        title = ""

        if mi == 0:
            title =  "Ground-truth"
        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), title)

        title = ""
        if mi == 0:
            title =  "Our result"
        plot_grid.showImage(setAlpha(C_32F, to32F(A_8U)), title)

        title = ""
        if mi == 0:
            title = "Error (shading)"
        plot_grid.showColorMap(C_error, title, v_min=0, v_max=0.1, with_colorbar=True)

        title = ""
        if mi == 0:
            title =  "Ground-truth"
        plot_grid.showImage(normalToColor(Ng_32F, A_8U), title)

        title = ""
        if mi == 0:
            title = "Our result"
        plot_grid.showImage(normalToColor(N_32F, A_8U), title)

        title = ""
        if mi == 0:
            title = "Error (shape)"

        plot_grid.showColorMap(N_error, title, v_min=0, v_max=50.0, with_colorbar=True)

    #showMaximize()
    file_path = shapeResultFile("ShapeEstimation", "MaterialShapeEvaluation", file_ext=".pdf")
    fig.savefig(file_path, transparent=False)


def estimatedReflectance(C0_32F, L, N_32F, A_8U):
    LdN = LdotN(L, N_32F)

    layer_area = A_8U > 0.5 * np.max(A_8U)
    Cs = C0_32F[layer_area].reshape(-1, 3)
    Is = LdN[layer_area].flatten()
    M = ColorMapEstimation(Cs, Is)
    return M

def reflectanceMatching(C0_32F, L, N_32F, A_8U):
    LdN = LdotN(L, N_32F)
    M = estimatedReflectance(C0_32F, L, N_32F, A_8U)
    C_32F = M.shading(LdN.flatten()).reshape(C0_32F.shape)
    return C_32F


def lumoSFS(C0_32F, L, N0_32F, A_8U):
    C_32F = reflectanceMatching(C0_32F, L, N0_32F, A_8U)
    return C_32F, N0_32F


def wuSFS(C0_32F, L, N0_32F, A_8U):
    wu_sfs = Wu08SFS(L, C0_32F, A_8U)
    wu_sfs.setInitialNormal(N0_32F)
    wu_sfs.setNumIterations(iterations=20)
    wu_sfs.setWeights(w_lap=1.0)
    wu_sfs.run()

    N_32F = wu_sfs.normal()
    C_32F = reflectanceMatching(C0_32F, L, N_32F, A_8U)
    return C_32F, N_32F


def computeErrors(L, C0_32F, C_32F, Ng_32F, N_32F, A_8U):
    h, w = A_8U.shape
    N_error = angleErros(N_32F.reshape(-1, 3), Ng_32F.reshape(-1, 3)).reshape(h, w)
    N_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
    N_error = trim(N_error, A_8U)

    C_error = normVectors(C0_32F.reshape(-1, 3) - C_32F.reshape(-1, 3)).reshape(h, w)
    C_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
    C_error = trim(C_error, A_8U)

    I_32F = np.clip(LdotN(L, N_32F), 0.0, 1.0)
    Ig_32F = np.clip(LdotN(L, Ng_32F), 0.0, 1.0)
    I_error = np.abs(I_32F - Ig_32F)
    I_error[A_8U < 0.5 * np.max(A_8U)] = 0.0
    I_error = trim(I_error, A_8U)
    return C_error, N_error, I_error

def computeIllumination(L, N_32F, A_8U):
    I_32F = np.clip(LdotN(L, N_32F), 0.0, 1.0)
    I_32F[A_8U < 0.5 * np.max(A_8U)] = 0.0
    I_32F = setAlpha(gray2rgb(to8U(I_32F)), A_8U)
    I_32F = trim(I_32F, A_8U)
    return I_32F


def materialErrorTable():
    shape_name = "ThreeBox"

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    num_materials = len(colorMapFiles())
    C_errors = np.zeros((num_materials, 3))
    N_errors = np.zeros((num_materials, 3))
    I_errors = np.zeros((num_materials, 3))

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data
    A_8U = cv2.bilateralFilter(A_8U, 0, 5, 2)

    for mi, color_map_file in enumerate(colorMapFiles()):
        M_32F = loadColorMap(color_map_file)

        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        toon_sfs = ToonSFS(L, C0_32F, A_8U)
        toon_sfs.setInitialNormal(N0_32F)
        toon_sfs.setNumIterations(iterations=20)
        toon_sfs.setWeights(w_lap=9.0)
        toon_sfs.run()

        N_toon = toon_sfs.normal()
        C_toon = toon_sfs.shading()

        C_lumo, N_lumo = lumoSFS(C0_32F, L, N0_32F, A_8U)
        C_wu, N_wu = wuSFS(C0_32F, L, N0_32F, A_8U)

        C_error_toon, N_error_toon, I_error_toon = computeErrors(L, C0_32F, C_toon, Ng_32F, N_toon, A_8U)
        C_error_lumo, N_error_lumo, I_error_lumo = computeErrors(L, C0_32F, C_lumo, Ng_32F, N_lumo, A_8U)
        C_error_wu, N_error_wu, I_error_wu = computeErrors(L, C0_32F, C_wu, Ng_32F, N_wu, A_8U)

        C_errors[mi, 0] = np.mean(C_error_toon)
        C_errors[mi, 1] = np.mean(C_error_lumo)
        C_errors[mi, 2] = np.mean(C_error_wu)

        I_errors[mi, 0] = np.mean(I_error_toon)
        I_errors[mi, 1] = np.mean(I_error_lumo)
        I_errors[mi, 2] = np.mean(I_error_wu)

        N_errors[mi, 0] = np.mean(N_error_toon)
        N_errors[mi, 1] = np.mean(N_error_lumo)
        N_errors[mi, 2] = np.mean(N_error_wu)

    file_path = shapeResultFile("ShapeEstimation", "MaterialShadingError", file_ext=".npy")
    np.save(file_path, C_errors)

    file_path = shapeResultFile("ShapeEstimation", "MaterialNormalError", file_ext=".npy")
    np.save(file_path, N_errors)

    file_path = shapeResultFile("ShapeEstimation", "MaterialIlluminationError", file_ext=".npy")
    np.save(file_path, I_errors)


def showMaterialErrorTable():

    M_error_order = reflectanceErrorOrders()

    def saveFigure(errors, title, file_name):
        w = 12
        h = 4
        fig, axes = plt.subplots(figsize=(w, h))
        fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.15)
        font_size = 15
        plt.title(title)
        plt.plot(errors[M_error_order, 2], label="Lambert assumption")
        plt.plot(errors[M_error_order, 1], label="Lumo")
        plt.plot(errors[M_error_order, 0], label="Our result")
        plt.xlabel("Material dataset")
        plt.ylabel("Error")
        plt.legend()

        file_path = shapeResultFile("ShapeEstimation", file_name, file_ext=".png")
        fig.savefig(file_path, transparent=True)

        print np.argmax(errors[M_error_order, 0] - errors[M_error_order, 2])
        print np.argmin(errors[M_error_order, 0] - errors[M_error_order, 2])


    file_path = shapeResultFile("ShapeEstimation", "MaterialShadingError", file_ext=".npy")
    C_errors = np.load(file_path)

    saveFigure(C_errors, "Shading Error",  "MaterialShadingError")

    file_path = shapeResultFile("ShapeEstimation", "MaterialNormalError", file_ext=".npy")
    N_errors = np.load(file_path)

    saveFigure(N_errors, "Shape Error",  "MaterialNormalError")

    file_path = shapeResultFile("ShapeEstimation", "MaterialIlluminationError", file_ext=".npy")
    I_errors = np.load(file_path)

    saveFigure(I_errors, "Illumination Error",  "MaterialIlluminationError")


def materialList():
    shape_name = "ThreeBox"
    num_rows = 1
    num_cols = len(colorMapFiles())

    w = 24
    h = w * num_rows / num_cols

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04, hspace=0.1, wspace=0.05)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    for colormap_file in colorMapFilesSortedReflectanceError():
        M_32F = loadColorMap(colormap_file)


        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "")

    file_path = shapeResultFile("ShapeEstimation", "MaterialList")
    fig.savefig(file_path, transparent=True)


def shapeErrorTable():
    cmap_id = 10
    colormap_file = colorMapFile(cmap_id)
    M_32F = loadColorMap(colormap_file)

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    num_shapes = len(shapeNames())
    C_errors = np.zeros((num_shapes, 3))
    N_errors = np.zeros((num_shapes, 3))
    I_errors = np.zeros((num_shapes, 3))

    for si, shape_name in enumerate(shapeNames()):
        Ng_data = shapeFile(shape_name)
        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
        N0_data = loadNormal(N0_file)
        N0_32F, A_8U = N0_data
        A_8U = cv2.bilateralFilter(A_8U, 0, 5, 2)
        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        toon_sfs = ToonSFS(L, C0_32F, A_8U)
        toon_sfs.setInitialNormal(N0_32F)
        toon_sfs.setNumIterations(iterations=20)
        toon_sfs.setWeights(w_lap=9.0)
        toon_sfs.run()

        N_toon = toon_sfs.normal()
        C_toon = toon_sfs.shading()

        C_lumo, N_lumo = lumoSFS(C0_32F, L, N0_32F, A_8U)
        C_wu, N_wu = wuSFS(C0_32F, L, N0_32F, A_8U)

        C_error_toon, N_error_toon, I_error_toon = computeErrors(L, C0_32F, C_toon, Ng_32F, N_toon, A_8U)
        C_error_lumo, N_error_lumo, I_error_lumo = computeErrors(L, C0_32F, C_lumo, Ng_32F, N_lumo, A_8U)
        C_error_wu, N_error_wu, I_error_wu = computeErrors(L, C0_32F, C_wu, Ng_32F, N_wu, A_8U)

        C_errors[si, 0] = np.mean(C_error_toon)
        C_errors[si, 1] = np.mean(C_error_lumo)
        C_errors[si, 2] = np.mean(C_error_wu)

        I_errors[si, 0] = np.mean(I_error_toon)
        I_errors[si, 1] = np.mean(I_error_lumo)
        I_errors[si, 2] = np.mean(I_error_wu)

        N_errors[si, 0] = np.mean(N_error_toon)
        N_errors[si, 1] = np.mean(N_error_lumo)
        N_errors[si, 2] = np.mean(N_error_wu)

    file_path = shapeResultFile("ShapeEstimation", "ShapeShadingError", file_ext=".npy")
    np.save(file_path, C_errors)

    file_path = shapeResultFile("ShapeEstimation", "ShapeNormalError", file_ext=".npy")
    np.save(file_path, N_errors)

    file_path = shapeResultFile("ShapeEstimation", "ShapeIlluminationErrorShape", file_ext=".npy")
    np.save(file_path, I_errors)

    showShapeErrorTable()


def showShapeErrorTable():

    def saveFigure(errors, title, file_name):
        w = 12
        h = 4
        fig, axes = plt.subplots(figsize=(w, h))
        fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.15)
        font_size = 15
        plt.title(title)
        plt.plot(errors[:, 2], label="Lambert assumption")
        plt.plot(errors[:, 1], label="Lumo")
        plt.plot(errors[:, 0], label="Our result")
        plt.xlabel("Shape dataset")
        plt.ylabel("Error")
        plt.legend()

        file_path = shapeResultFile("ShapeEstimation", file_name, file_ext=".png")
        fig.savefig(file_path, transparent=True)

        print shapeFiles()[np.argmax(errors[:, 0] - errors[:, 2])]
        print shapeFiles()[np.argmin(errors[:, 0] - errors[:, 2])]


    file_path = shapeResultFile("ShapeEstimation", "ShapeShadingError", file_ext=".npy")
    C_errors = np.load(file_path)

    saveFigure(C_errors, "Shading Error",  "ShapeShadingError")

    file_path = shapeResultFile("ShapeEstimation", "ShapeNormalError", file_ext=".npy")
    N_errors = np.load(file_path)

    saveFigure(N_errors, "Shape Error",  "ShapeNormalError")

    file_path = shapeResultFile("ShapeEstimation", "ShapeIlluminationErrorShape", file_ext=".npy")
    I_errors = np.load(file_path)

    saveFigure(I_errors, "Illumination Error",  "ShapeIlluminationError")


def shapeList():

    num_rows = 1
    num_cols = len(shapeNames())

    w = 20
    h = w * num_rows / num_cols

    cmap_id = 10
    colormap_file = colorMapFile(cmap_id)
    M_32F = loadColorMap(colormap_file)

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04, hspace=0.15, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    for shape_name in shapeNames():
        Ng_data = shapeFile(shape_name)
        Ng_data = loadNormal(Ng_data)
        Ng_32F, A_8U = Ng_data

        C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

        plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "")

    file_path = shapeResultFile("ShapeEstimation", "ShapeList")
    fig.savefig(file_path, transparent=True)

def methodComparisonFigure(shape_name="ThreeBox", cmap_id=10):
    num_methods = 3
    num_rows = 3
    num_cols = 2 * num_methods + 1

    w = 20
    h = w * num_rows / num_cols

    fig, axes = plt.subplots(figsize=(w, h))
    font_size = 15
    fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.04, hspace=0.15, wspace=0.1)
    fig.suptitle("", fontsize=font_size)

    plot_grid = SubplotGrid(num_rows, num_cols)

    L = normalizeVector(np.array([-0.4, 0.5, 0.6]))

    Ng_data = shapeFile(shape_name)
    Ng_data = loadNormal(Ng_data)
    Ng_32F, A_8U = Ng_data

    N0_file = shapeResultFile(result_name="InitialNormal", data_name=shape_name)
    N0_data = loadNormal(N0_file)
    N0_32F, A_8U = N0_data
    A_8U = cv2.bilateralFilter(A_8U, 0, 5, 2)

    colormap_file = colorMapFile(cmap_id)
    M_32F = loadColorMap(colormap_file)
    C0_32F = ColorMapShader(M_32F).diffuseShading(L, Ng_32F)

    toon_sfs = ToonSFS(L, C0_32F, A_8U)
    toon_sfs.setInitialNormal(N0_32F)
    toon_sfs.setNumIterations(iterations=100)
    toon_sfs.setWeights(w_lap=0.1)
    toon_sfs.run()

    N_toon = toon_sfs.normal()
    C_toon = toon_sfs.shading()

    C_lumo, N_lumo = lumoSFS(C0_32F, L, N0_32F, A_8U)
    C_wu, N_wu = wuSFS(C0_32F, L, N0_32F, A_8U)

    C_error_toon, N_error_toon, I_error_toon = computeErrors(L, C0_32F, C_toon, Ng_32F, N_toon, A_8U)
    C_error_lumo, N_error_lumo, I_error_lumo = computeErrors(L, C0_32F, C_lumo, Ng_32F, N_lumo, A_8U)
    C_error_wu, N_error_wu, I_error_wu = computeErrors(L, C0_32F, C_wu, Ng_32F, N_wu, A_8U)

    plot_grid.showImage(setAlpha(C0_32F, to32F(A_8U)), "Ground-truth")

    title = ""
    plot_grid.showImage(setAlpha(C_lumo, to32F(A_8U)), "Lumo")
    plot_grid.showColorMap(C_error_lumo, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_wu, to32F(A_8U)), "Lambert assumption")
    plot_grid.showColorMap(C_error_wu, title, v_min=0, v_max=0.1, with_colorbar=True)
    plot_grid.showImage(setAlpha(C_toon, to32F(A_8U)), "Our result")
    plot_grid.showColorMap(C_error_toon, title, v_min=0, v_max=0.1, with_colorbar=True)

    plot_grid.showImage(normalToColor(Ng_32F, A_8U), title)

    plot_grid.showImage(normalToColor(N_lumo, A_8U), title)
    plot_grid.showColorMap(N_error_lumo, title, v_min=0, v_max=50.0, with_colorbar=True)
    plot_grid.showImage(normalToColor(N_wu, A_8U), title)
    plot_grid.showColorMap(N_error_wu, title, v_min=0, v_max=50.0, with_colorbar=True)
    plot_grid.showImage(normalToColor(N_toon, A_8U), title)
    plot_grid.showColorMap(N_error_toon, title, v_min=0, v_max=50.0, with_colorbar=True)

    plot_grid.showImage(computeIllumination(L, Ng_32F, A_8U), title)

    plot_grid.showImage(computeIllumination(L, N_lumo, A_8U), title)
    plot_grid.showColorMap(I_error_lumo, title, v_min=0, v_max=0.2, with_colorbar=True)
    plot_grid.showImage(computeIllumination(L, N_wu, A_8U), title)
    plot_grid.showColorMap(I_error_wu, title, v_min=0, v_max=0.2, with_colorbar=True)
    plot_grid.showImage(computeIllumination(L, N_toon, A_8U), title)
    plot_grid.showColorMap(I_error_toon, title, v_min=0, v_max=0.2, with_colorbar=True)

    # showMaximize()
    file_path = shapeResultFile("ShapeEstimation", "Comparison_%s_%s" %(shape_name, cmap_id), file_ext=".png")
    fig.savefig(file_path, transparent=True)

if __name__ == '__main__':
    LambertShadingFigure()
    #methodComparisonFigure(shape_name="Ogre", cmap_id=5)
    #materialList()
    #showMaterialErrorTable()
    # showShapeErrorTable()
