import csv

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plot

import schurtransform as st
from schurtransform.transform import SchurTransform

def grab_from_4DCT(case):
    filenames=[
    "example_data/case"+case+"_4D-75_T00.txt",
    "example_data/case"+case+"_4D-75_T10.txt",
    "example_data/case"+case+"_4D-75_T20.txt",
    "example_data/case"+case+"_4D-75_T30.txt",
    "example_data/case"+case+"_4D-75_T40.txt",
    "example_data/case"+case+"_4D-75_T50.txt"]
    X = []
    if(case == "0"):
        for i in range(len(filenames)):
            X.append([])
            with open("example_data/case1_4D-75_T00.txt") as file:
                reader = csv.reader(file)
                for row in reader:
                    X[i].append([float(val) for val in row])
    else:
        for i,filename in enumerate(filenames):
            X.append([])
            with open(filename) as file:
                reader = csv.reader(file)
                for row in reader:
                    X[i].append([float(val) for val in row])
    return np.array(X)

def single_log_scale(val):
    if(val!=0):
        return np.log(val)
    else:
        return -float('Inf')

number_of_factors = 3
sc1 = st.transform(x1, summary_type=SummaryType.CONTENT, number_of_factors=number_of_factors)
schurcontent = str(number_of_factors)+"-factor Schur content (log scale)"
modes = list(sc1.keys())
d = {schurcontent: [], "Mode (Sn conjugacy class representative)": [],"Case": []}
for i in range(5):
    xi = grab_from_4DCT(str(i+1))
    sc = st.transform(xi, summary_type='CONTENT', number_of_factors=number_of_factors)
    for key in sc1.keys():
        for value in sc1[key]:
            d[schurcontent].append(single_log_scale(value))
            d["Mode (Sn conjugacy class representative)"].append('mode ' + str(key))
            d["Case"].append('case ' + str(i+1))
    print("Finished case "+str(i+1)+" of "+str(5)+".")

df = pd.DataFrame(data=d)

schurcontentseq = "Sequential "+str(number_of_factors)+"-factor Schur content (log scale)"
dseq = {schurcontentseq: [], "Mode (Sn conjugacy class representative)": [],"Case": []}
for i in range(5):
    xi = grab_from_4DCT(str(i+1))
    sc = st.transform(xi, summary_type='SEQUENTIAL_CONTENT', number_of_factors=number_of_factors)
    for key in sc.keys():
        for value in sc[key]:
            dseq[schurcontentseq].append(single_log_scale(value))
            dseq["Mode (Sn conjugacy class representative)"].append('mode ' + str(key))
            dseq["Case"].append('case ' + str(i+1))
    print("Finished case "+str(i+1)+" of "+str(5)+". (Sequential version)")

df_sequential = pd.DataFrame(data=dseq)

# plot.rcParams.update({'font.size': 24})

fig = plot.figure(figsize=(7.5,5))
#ax = sns.violinplot(y="Mode (Sn conjugacy class representative)", x=schurcontent, data=df, inner="stick",scale="area",hue="Case",cut=0)
ax = sns.violinplot(y="Mode (Sn conjugacy class representative)", x=schurcontent, data=df,hue="Case")
plot.setp(ax.get_legend().get_title(), fontsize='22')
plot.ylabel('Mode (Sn conjugacy class representative)', fontsize=16)
plot.xlabel(schurcontent, fontsize=16)
ax.grid(False)
fig.add_axes(ax)

fig_seq = plot.figure(figsize=(7.5,5))
ax_seq = sns.violinplot(y="Mode (Sn conjugacy class representative)", x=schurcontentseq, data=df_sequential, inner="stick",scale="area",hue="Case",cut=0)
plot.setp(ax_seq.get_legend().get_title(), fontsize='22')
plot.ylabel('Mode (Sn conjugacy class representative)', fontsize=16)
plot.xlabel(schurcontentseq, fontsize=16)
ax_seq.grid(False)
fig_seq.add_axes(ax_seq)

plot.show()



#x1 = grab_from_4DCT('1')

#st.transform(x1, summary_type='CONTENT', number_of_factors=3)
