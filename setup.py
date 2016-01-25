# -*- coding: utf-8 -*-
## @package setup
#
#  setup utility package.
#  @author      tody
#  @date        2015/08/14

from setuptools import setup, find_packages
from ivf import __author__, __version__, __license__

setup(
        name = 'ivf',
        version = __version__,
        description = 'Simple framework to develop a 2D Image Viewer with Python.',
        license = __license__,
        author = __author__,
        url = 'https://github.com/tody411/ImageViewerFramework.git',
        packages = find_packages(),
        install_requires = ['docopt'],
        )

