"""
@author: wangye(Wayne)
@license: Apache Licence
@file: load_data.py
@time: 20230204
@contact: wang121ye@hotmail.com
@site:  wangyendt@github.com
@software: PyCharm

# code is far away from bugs.
"""

from config import PATH
import pandas as pd
import numpy as np


def load_time_consumption_data():
    """
    A dict, where key is the function name and value is the function elapsed time over all frames.
    :return: { str:np.ndarray(Nx2) }
    """
    data = pd.read_csv(PATH)
    time_span = [data['timestamp'].values[0], data['timestamp'].values[-1]]
    data['item'] = data['function'].apply(lambda x: x.split('_')[-1])
    data = data[['timestamp', 'elapsed_time(ms)', 'item']]
    data['time'] = data.apply(lambda x: [x['timestamp'], x['elapsed_time(ms)']], axis=1)
    data = data.drop(['timestamp', 'elapsed_time(ms)'], axis=1)
    data = data.groupby('item').agg({'time': list}).T.to_dict()
    data = {k: np.array(v['time']) for k, v in data.items()}
    return data, time_span


if __name__ == '__main__':
    import matplotlib

    matplotlib.use('MacOSX')
    import matplotlib.pyplot as plt

    data, time_span = load_time_consumption_data()
    print(data.keys())
    print(time_span)
    item = data['ComputeKeyPointsOctTree']
    plt.plot(item[:, 0], item[:, 1])
    plt.grid(True)
    plt.show()
