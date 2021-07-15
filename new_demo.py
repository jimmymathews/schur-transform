import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plot

import schurtransform as st

def single_log_scale(val):
    if(val!=0):
        return np.log(val)
    else:
        return -float('Inf')

def get_dataframe_representation(cases, title):
    records = [
        [single_log_scale(value), mode, str(case_number)]
        for case_number, content_by_mode in cases.items()
        for mode, content in content_by_mode.items()
        for value in content
    ]
    return pd.DataFrame(
        records,
        columns = [title, 'Mode', 'Case'],
    )

number_of_factors = 3
data = st.get_example_data(dataset = 'lung 4DCT')
modes = list(st.transform(data[0], summary='CONTENT', number_of_factors=number_of_factors).keys())

title = str(number_of_factors) + '-factor Schur content (log scale)'
cases = {}
for i, x in enumerate(data):
    cases[i] = st.transform(x, summary='CONTENT', number_of_factors=number_of_factors)

title_sequential = 'Sequential ' + str(number_of_factors) + '-factor Schur content (log scale)'
cases_sequential = {}
for i, x in enumerate(data):
    cases_sequential[i] = st.transform(x, summary='SEQUENTIAL_CONTENT', number_of_factors=number_of_factors)

content_dataframe = get_dataframe_representation(cases, title)
sequential_content_dataframe = get_dataframe_representation(cases_sequential, title_sequential)

fig = plot.figure(figsize=(7.5,5))
ax = sns.violinplot(y='Mode', x=title, data=content_dataframe, inner='stick', scale='area', hue='Case', cut=0)
plot.setp(ax.get_legend().get_title(), fontsize=12)
ax.grid(False)
fig.add_axes(ax)

fig_sequential = plot.figure(figsize=(7.5,5))
ax_sequential = sns.violinplot(y='Mode', x=title_sequential, data=sequential_content_dataframe, inner='stick', scale='area', hue='Case', cut=0)
plot.setp(ax_sequential.get_legend().get_title(), fontsize=12)
ax_sequential.grid(False)
fig_sequential.add_axes(ax_sequential)

plot.show()
