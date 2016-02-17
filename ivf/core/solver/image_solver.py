
# -*- coding: utf-8 -*-
## @package ivf.core.solver.image_solver
#
#  ivf.core.solver.image_solver utility package.
#  @author      tody
#  @date        2016/02/09

import numpy as np
import cv2
from ivf.util.timer import timing_func


def laplacian(image):
    image_L = laplacianCV(image)
    return image_L


def laplacianCV(image):
    return cv2.Laplacian(image, cv2.CV_64F) / 4.0


def pyrDown(image, image_size=None):
    if image_size is None:
        h, w = image.shape[:2]
        image_size = w/2, h/2
    return cv2.resize(image, image_size)


def pyrUp(image, image_size=None):
    if image_size is None:
        h, w = image.shape[:2]
        image_size = w*2, h*2
    return cv2.resize(image, image_size)


def solve(image, solve_iter, iterations=10, tol=1e-8):
    image_new = np.array(image)
    image_new = solve_iter(image_new, iterations, tol)
    return image_new


def solveMG(image, solve_iter, iterations=10, tol=1e-4, low_level=16):
    h, w = image.shape[:2]
    image_size_min = min(h, w)

    image_level = np.array(image)

    num_level = 0
    while image_size_min > low_level:
        image_level = pyrDown(image_level)
        h, w = image_level.shape[:2]
        image_size_min = min(h, w)
        print image_size_min
        num_level += 1

    for level in xrange(num_level-1):
        # level_iterations = 2 ** (num_level - level) * iterations
        level_iterations = iterations
        image_level = solve_iter(image_level, level_iterations, tol)
        image_level = pyrUp(image_level)

    h, w = image.shape[:2]
    image_level = pyrUp(image_level, image_size=(w, h))
    image_level = solve_iter(image_level, iterations, tol)
    return image_level


class LevelImage:
    def __init__(self, image):
        self._image = image
        self._image_level = np.array(image)

    def level(self, guide_image):
        if self._image_level.shape[0] != guide_image.shape[0]:
            h, w = guide_image.shape[:2]
            self._image_level = pyrDown(self._image, (w, h))
        return self._image_level


def solveIterator(constraint_funcs=[], post_funcs=[]):
    def func(image, iterations=10, tol=1e-8):
        for i in xrange(iterations):
            image_new = np.zeros(image.shape)

            w_sum = 0.0
            for constraint_func in constraint_funcs:
                w_c, image_c = constraint_func(image)
                image_new += w_c * image_c
                w_sum += w_c

            if w_sum > 0.0:
                image_new *= 1.0 / w_sum

            for post_func in post_funcs:
                image_new = post_func(image_new)

            error = np.linalg.norm(image_new - image) / np.linalg.norm(image)

            print "Iteration%i: %s" %(i, error)

            image = image_new

            if error < tol:
                break

        return image
    return func