
# -*- coding: utf-8 -*-
## @package ivf.io_util.dict_data
#
#  Dictionary data IO utility package.
#  @author      tody
#  @date        2015/10/27


import json


def loadDict(file_path):
    with open(file_path, 'r') as f:
        json_data = f.read()
        data = json.loads(json_data)
        return data

    return None


def saveDict(file_path, data):
    with open(file_path, 'w') as f:
        f.write(json.dumps(data))
