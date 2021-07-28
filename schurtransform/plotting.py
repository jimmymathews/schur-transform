import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re

from .log_formats import colorized_logger
logger = colorized_logger(__name__)

def convert_to_log_scale(val):
    if(val!=0):
        return np.log(val)
    else:
        return -float('Inf')

def get_dataframe_representation(transform_data):
    """
    :param transform_data: As output from
        :py:meth:`.schur_transform.SchurTransform.transform`.
    :type transform_data: dict

    :return: Convenience function that returns a dataframe representation of the
        transformed data (content), with columns ['Component norms','Mode','Case'].
    :rtype: pandas.DataFrame
    """
    records = [
        [convert_to_log_scale(value), mode, str(case_number)]
        for case_number, content_by_mode in transform_data.items()
        for mode, content in content_by_mode.items()
        for value in content
    ]
    return pd.DataFrame(
        records,
        columns = ['Component norms', 'Mode', 'Case'],
    )

def infer_degree_from_transform_data(transform_data):
    """
    :param transform_data: As output from
        :py:meth:`.schur_transform.SchurTransform.transform`.
    :type transform_data: dict

    :return: Recovers the number of tensor factors put into the transform, i.e. the
        degree of the symmetric group involved.
    :rtype: int
    """
    keys = transform_data.keys()
    modes = transform_data[list(keys)[0]].keys()
    trivial_element = ''
    for partition in modes:
        partition = str(partition)
        if re.match(r'^(1\+)+1$', partition):
            trivial_element = partition
            break
    return len(trivial_element.split('+'))

def create_figure(transform_data, summary=None, ax=None):
    """
    :param transform_data: As output from
        :py:meth:`.schur_transform.SchurTransform.transform`.
    :type transform_data: dict

    :param summary: The name of the :py:class:`.schur_transform.DecompositionSummary`
        used to perform the transform. For this plotting function, the ``summary``
        value must be either ``CONTENT`` or ``SEQUENTIAL_CONTENT``.
    :type summary: str

    :param ax: If provided, this method will not generate a new figure and axes but
        will rather plot to the provided axes.
    :type ax: matplotlib.Axes

    :return: [fig, ax] The matplotlib figure and axes (if created anew).
    :rtype: list
    """
    content_dataframe = get_dataframe_representation(transform_data)
    presentation_names = {
        'CONTENT' : 'Schur content',
        'SEQUENTIAL_CONTENT' : 'sequential Schur content',
    }
    if summary in presentation_names:
        presentation_name = presentation_names[summary]
    else:
        if summary is None:
            logger.error('Must specify "summary".')
        else:
            logger.error('Summary type %s not supported in figure generation yet. Try a heatmap?', summary)
        return
    number_of_factors = infer_degree_from_transform_data(transform_data)
    title = str(number_of_factors) + '-factor ' + presentation_name
    content_dataframe.rename(columns={'Component norms' : 'Component norms (log scale)'}, inplace=True)
    sns.set_theme(style='whitegrid')
    no_ax_supplied = ax is None
    if no_ax_supplied:
        fig = plt.figure(figsize=(7.5,5))
        ax = sns.violinplot(x='Mode', y='Component norms (log scale)', data=content_dataframe, inner='stick', scale='area', hue='Case', cut=0)
        fig.add_axes(ax)
    else:
        sns.violinplot(x='Mode', y='Component norms (log scale)', data=content_dataframe, inner='stick', scale='area', hue='Case', cut=0, ax=ax)
    plt.setp(ax.get_legend().get_title(), fontsize=10)
    ax.set_title(title)
    if no_ax_supplied:
        return [fig, ax]
    else:
        return None
