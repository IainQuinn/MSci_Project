import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.signal
import os
import pandas as pd
from natsort import index_natsorted
import glob
from itertools import chain
import csv
from itertools import cycle

molecule = 'diethylether'

ROOT_DIR = f'/users/ekb16170/msci_project/rism/combinations/diethylether/'
RDF_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/diethylether_iain_done/'
SAVE_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/save_dir/'

mdl_name_list = []
max_val_list = []
rel_dis_list = []

for mdl in os.listdir(f'{ROOT_DIR}'):
	if f'{molecule}_' in mdl:
		#print(mdl)

		for gvv in os.listdir(f'{ROOT_DIR}/{mdl}'):
			name, ext = os.path.splitext(gvv)
		
			if ext == '.gvv':
				mdl_name = mdl.split('_')[1]
				mdl_name_list.append(mdl_name)				

				try:
					data = pd.read_csv(f'{ROOT_DIR}/{mdl}/{molecule}.gvv', delim_whitespace=True)
					column_titles = ['#RISM1D', 'ATOM-ATOM']
					data = data.reindex(columns=column_titles)
					data.columns = ['Distance(Å)', 'g(r)']
					sorted_data = data.drop(data.index[0:4])
					sorted_data = sorted_data.astype(float)
					sorted_data_gvv = sorted_data.iloc[120:566] #only uses part of wave approximately around well
					#plt.plot(sorted_data_gvv['Distance(Å)'], sorted_data_gvv['Energy(kT)'])
			
					max_val = max(sorted_data_gvv['g(r)'])
					max_val_list.append(float(max_val))

					rel_dis_row = sorted_data_gvv['g(r)'].argmax()
					rel_dis = sorted_data_gvv['Distance(Å)'].iloc[rel_dis_row]
					#print(rel_dis)
					rel_dis_list.append(float(rel_dis))

				except FileNotFoundError:
					continue

#plt.show()

mdl_dict = {'mdl':mdl_name_list, 'mdl_max_energy':max_val_list, 'mdl_rel_distance':rel_dis_list}
mdl_df = pd.DataFrame(mdl_dict)
#print(mdl_df)

data_rdf = pd.read_csv(f'{RDF_DIR}/rdf.xvg', delim_whitespace=True)
data_rdf.columns = ['Distance(nm)', 'g(r)']
data_rdf = data_rdf.astype(float)
data_rdf['Distance(Å)'] = data_rdf['Distance(nm)'] * 10
max_val_rdf = max(data_rdf['g(r)'])
max_val_rdf = float(max_val_rdf)
rdf_rel_dis_row = data_rdf['g(r)'].argmax()
rdf_rel_dis = data_rdf['Distance(Å)'].iloc[rdf_rel_dis_row]
#print(rel_dis)

mdl_df['rdf_max_energy'] = max_val_rdf 
mdl_df['rdf_ref_distance'] = rdf_rel_dis 
mdl_df['rdf_max_energy'] = mdl_df.rdf_max_energy.astype(float)
mdl_df['rdf_ref_distance'] = mdl_df.rdf_ref_distance.astype(float)
mdl_df['energy_dif'] = mdl_df['rdf_max_energy'] - mdl_df['mdl_max_energy']
mdl_df['distance_dif'] = mdl_df['rdf_ref_distance'] - mdl_df['mdl_rel_distance']
mdl_df['rdf_max_energy'].iloc[1:] = ''
mdl_df['rdf_ref_distance'].iloc[1:] = ''
mdl_df['sorted_energy_dif'] = mdl_df['energy_dif'].abs()
mdl_df['sorted_distance_dif'] = mdl_df['distance_dif'].abs()

mdl_df['sorted_true_dif'] = mdl_df['sorted_energy_dif'] - mdl_df['sorted_distance_dif']
mdl_df['sorted_true_dif'] = np.sqrt(((mdl_df['sorted_energy_dif'])**2) + ((mdl_df['sorted_distance_dif'])**2)) 

mdl_df = mdl_df.sort_values(by=['sorted_true_dif'])
#print(mdl_df)
cycol = cycle('bgr')

for num in mdl_df['mdl'][0:3]: #compares MD rdf to the 3 most comparable CG rdf
	print(num)
	
	for mdl in os.listdir(f'{ROOT_DIR}'):
		mdl_num = mdl.split('_')[1]
		if mdl_num == num:

			num_data = pd.read_csv(f'{ROOT_DIR}/{molecule}_{num}/{molecule}.gvv', delim_whitespace=True)
			column_titles = ['#RISM1D', 'ATOM-ATOM']
			num_data = num_data.reindex(columns=column_titles)
			num_data.columns = ['Distance(Å)', 'g(r)']
			sorted_num_data = num_data.drop(num_data.index[0:4])
			sorted_num_data = sorted_num_data.astype(float)
			#sorted_num_data['Energy(kcal/mol)'] = sorted_num_data['Energy(kT)'] * 0.583
			sorted_num_data_gvv = sorted_num_data.iloc[120:800] #only uses part of wave approximately around well
			plt.plot(sorted_num_data_gvv['Distance(Å)'], sorted_num_data_gvv['g(r)'], c=next(cycol), label=f'CG Model {num}')

yhat = scipy.signal.savgol_filter(data_rdf['g(r)'], 51, 3)
plt.plot(data_rdf['Distance(Å)'], yhat,  color='black', label='Atomistic (MD)')

plt.xlabel('Distance (Å)')
plt.ylabel('g(r)')
plt.legend(title = 'Plot',loc='best', fancybox=True, shadow=True)
plt.title("Atomistic MD RDF Vs The 3 Closest Matching CG RDF's")
plt.xlim(0, 20)
plt.ylim(0, 2.0)
fig = plt.gcf()
plt.show()
fig.savefig(f'{SAVE_DIR}rdf_vs_gvv.png', dpi=1000)

os.chdir(SAVE_DIR)
#mdl_df.to_csv('rdf_vs_gvv.csv', index=False)

