
Image Viewer Framework (Python)
====

This package provides a simple framework to develop a 2D Image Viewer with C++ on Windows.

## Installation

*Note*: This program was only tested on **Windows** with **Python2.7**.
**Linux** and **Mac OS** are not officially supported,
but the following instructions might be helpful for installing on those environments.

### Dependencies
Please install the following required python modules.

* **NumPy**
* **SciPy**
* **matplotlib**
* **OpenCV**

As these modules are heavily dependent on NumPy modules, please install appropriate packages for your development environment (Python versions, 32-bit or 64-bit).
For 64-bit Windows, you can download the binaries from [**Unofficial Windows Binaries for Python Extension Packages**](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

<!-- This program also uses **docopt** for CLI.
**docopt** will be installed automatically through the following **pip** command for main modules. -->

### Install main modules

You can use **pip** command for installing main modules.
Please run the following command from the shell.

``` bash
  > pip install git+https://github.com/tody411/ImageViewerFramework.git
```

## Usage
### Run Demo

* [```ivf/main.py```](ivf/main.py):

You can test the demo with the following command from ```ivf``` directory.
``` bash
  > python main.py
```

This command will run the GUI application.


## License

The MIT License 2016 (c) tody