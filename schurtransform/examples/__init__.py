import importlib.resources

import pandas as pd

from .. import lung_data

def get_example_data(dataset: str=None):
    """
    :param dataset:
        Use 'lung 4DCT' for a `dataset <https://www.dir-lab.com>`_ of registered
        point locations annotated on CT scans of a lung breathing motion. 
    :type dataset: str

    :return:
        Each element is a list of lists of lists. The shape of each such 3-fold
        array is (6, 75, 3), indicating that the array consists 75 3-dimensional
        points registered across 6 time steps.
    :rtype: list
    """
    with importlib.resources.path(package=lung_data, resource='examples_manifest.csv') as path:
        lung_file_metadata = pd.read_csv(path)

    if dataset == 'lung 4DCT':
        data_dict = {i : {} for i in range(6)}
        for i, row in lung_file_metadata.iterrows():
            filename = row['filename']
            with importlib.resources.path(package=lung_data, resource=filename) as path:
                points = pd.read_csv(path, header=None)
            [list(point) for i, point in points.iterrows()]
            case_number = int(row['case number'])
            time_step = int(row['time step'])
            data_dict[time_step][case_number] = points

        data = [[data_dict[time_step][case_number] for time_step in range(6)] for case_number in range(1,6)]
        return data
