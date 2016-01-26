
# -*- coding: utf-8 -*-
## @package ivf.scene.data
#
#  ivf.scene.data utility package.
#  @author      tody
#  @date        2016/01/26


from ivf.util.logger import getLogger
from ivf.io_util.dict_data import loadDict, saveDict
logger = getLogger(__name__)


## Base data definition.
class Data(object):
    ## Constructor
    def __init__(self):
        super(Data, self).__init__()

    #################
    # Data IO
    #################

    ## Save data to the output file (shared with derived classes).
    #  Note: implement _dataDict method in the derived class.
    def save(self, file_path):
        data = self._dataDict()
        if data is not None:
            saveDict(file_path, data)

    ## Load data from the input file (shared with derived classes).
    #  Note: implement _setDataDict method in the derived class.
    def load(self, file_path):
        data = loadDict(file_path)
        if data is not None:
            self._setDataDict(data)

    ## dictionary data for writeJson method.
    def _dataDict(self):
        logger.warning("Need to implement _dataDict function.")
        return None

    ## set dictionary data for loadJson method.
    def _setDataDict(self, data):
        logger.warning("Need to implement _setDataDict function.")
        pass
