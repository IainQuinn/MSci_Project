import numpy as np
from scipy import optimize
import scipy.signal
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import pandas as pd
from natsort import index_natsorted
import glob
from scipy.interpolate import make_interp_spline, BSpline

ROOT_DIR = '/users/ekb16170/msci_project/Gromacs/results_analysis/diethylether_iain_done/'
GVV_DIR = '/path/to/best/cg/model/rdf'
SAVE_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/save_dir/'

os.chdir(ROOT_DIR)

rdf = 'rdf.xvg' #change for whatever file im looking at

data = pd.read_csv(f'{rdf}', delim_whitespace=True)
data.columns = ['Distance(nm)', 'g(r)']
data = data.astype(float)
data['Distance(Å)'] = data['Distance(nm)'] * 10
x = data['Distance(Å)']
y = data['g(r)']
yhat = scipy.signal.savgol_filter(y, 51, 3)
plt.plot(x, yhat,  color='black', label='Atomistic')
plt.title("Atomistic Molecular Dynamics RDF")
plt.xlabel('Distance (Å)')
plt.ylabel('g(r)')
plt.xlim(0, 20)
plt.ylim(0, 2)


#gvv = 'chloroform.gvv' #change for whatever file im looking at

#data = pd.read_csv(f'{GVV_DIR}{gvv}', delim_whitespace=True)
#column_titles = ['#RISM1D', 'ATOM-ATOM']
#data = data.reindex(columns=column_titles)
#data.columns = ['Distance(ang)', 'Energy(kT)']
#sorted_data = data.drop(data.index[0:4])
#sorted_data = sorted_data.astype(float)
#sorted_data['Energy(kcal/mol)'] = sorted_data['Energy(kT)'] * 0.583
#sorted_data_gvv = sorted_data.iloc[135:1000] #only uses part of wave approximately around well
#plt.plot(sorted_data_gvv['Distance(ang)'], sorted_data_gvv['Energy(kT)'],  color='blue', label='Lennard-Jones')
#plt.xlabel('Distance (Å)')
#plt.ylabel('g(r)')
#plt.legend(loc='best')


plt.savefig(f'{SAVE_DIR}rdf_gvv_smoothed_iain.png', dpi=1000)
plt.show()

