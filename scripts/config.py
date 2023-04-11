"""
@author: wangye(Wayne)
@license: Apache Licence
@file: config.py
@time: 20230204
@contact: wang121ye@hotmail.com
@site:  wangyendt@github.com
@software: PyCharm

# code is far away from bugs.
"""

import os
import pkgutil

if pkgutil.find_loader("pywayne"):
    from pywayne.tools import list_all_files
    PATH = sorted(list_all_files('../example/running_time'), key=lambda x: os.path.getctime(x))[-1]
else:
    PATH = '../example/running_time/270909067.txt'
DEBUG = False
