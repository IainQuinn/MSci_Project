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
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from numpy import trapz



molecule = 'diethylether'
end = '_combinations_newgridB_tol-12_test'
closure = 'KH,PSE3'
functional = 'PC+'

ROOT_DIR = f'/users/ekb16170/msci_project/rism/combinations/diethylether/'
RDF_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/diethylether_iain_done/'
SAVE_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/save_dir/'
D_DIR = f'/users/ekb16170/msci_project/rism/3drism/diethylether/grid_search/diethylether_combinations/Results/{closure}_Results/'

os.chdir(SAVE_DIR)

mdl_name_list = []
int_list = []

for mdl in os.listdir(f'{ROOT_DIR}'):
	if f'{molecule}_' in mdl:
		#print(mdl_name)
		mdl_name_list.append(mdl)
		gvv_file = Path(f'{ROOT_DIR}/{mdl}/{molecule}.gvv')

		try:
			if gvv_file.is_file():
				data = pd.read_csv(f'{ROOT_DIR}/{mdl}/{molecule}.gvv', delim_whitespace=True)
				column_titles = ['#RISM1D', 'ATOM-ATOM']
				data = data.reindex(columns=column_titles)
				data.columns = ['Distance(Å)', 'g(r)']
				sorted_data = data.drop(data.index[0:4])
				sorted_data = sorted_data.astype(float)

				np_sorted_data_distance = np.array(sorted_data['Distance(Å)'])
				np_sorted_data_energy = np.array(sorted_data['g(r)'])
				#print(np_sorted_data_distance)
			
				x = 0.99
				start_energy_list = [i for i in np_sorted_data_energy if i > x]
				start_energy = float(start_energy_list[0])
				start_energy_index = np.where(np_sorted_data_energy == start_energy)
				start_energy_index = str(start_energy_index)
				start_energy_pos = start_energy_index[8:11]
				#print(start_energy_pos)
				
				stat_point = min(np_sorted_data_energy[int(start_energy_pos):])
				stat_point_index = np.where(np_sorted_data_energy == stat_point)
				stat_point_index  = str(stat_point_index)
				stat_point_pos = stat_point_index[8:11]
				#print(stat_point, stat_point_pos)

				area = trapz(np_sorted_data_energy[:int(stat_point_pos)], dx=0.025)
				int_list.append(float(area))
				#print(area)

			else:
				int_list.append(float('NaN'))

		except ValueError:
			continue

#print(mdl_name_list, int_list)

data_rdf = pd.read_csv(f'{RDF_DIR}/rdf.xvg', delim_whitespace=True)
data_rdf.columns = ['Distance(nm)', 'g(r)']
data_rdf = data_rdf.astype(float)
data_rdf['Distance(Å)'] = data_rdf['Distance(nm)'] * 10
#print(data_rdf)

np_sorted_data_distance_rdf = np.array(data_rdf['Distance(Å)'])
np_sorted_data_energy_rdf = np.array(data_rdf['g(r)'])
#print(np_sorted_data_distance)
			
x = 0.99
start_energy_list_rdf = [i for i in np_sorted_data_energy_rdf if i > x]
start_energy_rdf = float(start_energy_list_rdf[0])
start_energy_index_rdf = np.where(np_sorted_data_energy_rdf == start_energy_rdf)
start_energy_index_rdf = str(start_energy_index_rdf)
start_energy_pos_rdf = start_energy_index_rdf[8:11]
#print(start_energy_pos)
				
stat_point_rdf = min(np_sorted_data_energy_rdf[int(start_energy_pos_rdf):])
stat_point_index_rdf = np.where(np_sorted_data_energy_rdf == stat_point_rdf)
stat_point_index_rdf  = str(stat_point_index_rdf)
stat_point_pos_rdf = stat_point_index_rdf[8:11]
#print(stat_point, stat_point_pos)

area_rdf = trapz(np_sorted_data_energy_rdf[:int(stat_point_pos_rdf)], dx=0.02)
#print(area_rdf)

mdl_dict = {'Combinations':mdl_name_list, 'mdl_int':int_list, 'rdf_int':area_rdf}
mdl_df = pd.DataFrame(mdl_dict)
mdl_df['int_error'] = mdl_df['rdf_int'] - mdl_df['mdl_int']
mdl_df['rdf_int'].iloc[1:] = ''
mdl_df = mdl_df.sort_values(by=['Combinations'])
#print(mdl_df)

df = pd.read_csv(f'{D_DIR}{closure}_{functional}.csv')
df = df.sort_values(by=['Combinations'])
df = df.replace(np.nan, '0', regex=True)
df['No. of molecules that ran'] = df['No. of molecules that ran'].astype(float)
df.loc[df['No. of molecules that ran'] < 3, ['RMSE PC+']] = 'NaN' #remove results with fewer than x molecules that ran
df.loc[df['RMSE PC+'] == 'NaN', ['No. of molecules that ran']] = 'NaN'
#print(df)

#df.to_csv('test1.csv', index=False)
#mdl_df.to_csv('test2.csv', index=False)

merged_df = df.merge(mdl_df, how='right')
#print(merged_df)
#merged_df.to_csv('test.csv', index=False)

#merged_df = merged_df.sort_values(by=['sigma'])
#n = 40
#merged_df = merged_df.drop(merged_df.tail(n).index)
#merged_df = merged_df.sort_values(by=['Combinations'])
#print(merged_df)

merged_df_number = merged_df[['eps', 'sigma', 'int_error']].copy()
merged_df_number['eps'] = merged_df_number['eps'].apply(lambda x: float(x))
merged_df_number['sigma'] = merged_df_number['sigma'].apply(lambda x: float(x)) 
merged_df_number['sigma'] = merged_df_number['sigma'].round(2)
merged_df_number['int_error'] = merged_df_number['int_error'].apply(lambda x: float(x))
merged_df_number = merged_df_number.pivot(index='eps', columns='sigma', values='int_error')
#fig, ax = plt.subplots(figsize=(12, 12))
ax = sns.heatmap(merged_df_number, cbar=False, annot=True, annot_kws={'color': 'white',"size": 7}, cmap="viridis", vmin=0, vmax=1.75, fmt='.2g')
merged_df_error = merged_df[['eps', 'sigma', 'int_error']].copy()
merged_df_error['eps'] = merged_df_error['eps'].apply(lambda x: float(x))
merged_df_error['eps'] = merged_df_error['eps'].round(2)
merged_df_error['sigma'] = merged_df_error['sigma'].apply(lambda x: float(x)) 
merged_df_error['sigma'] = merged_df_error['sigma'].round(2)
merged_df_error['int_error'] = merged_df_error['int_error'].apply(lambda x: float(x))
merged_df_error = merged_df_error.pivot(index='eps', columns='sigma', values='int_error')
ax2 = sns.heatmap(merged_df_error, cbar_kws={'label': f'1st Solvation Shell Area Error'}, cmap="viridis", vmin=0, vmax=1.75, fmt='.1g')
ax2.set(xlabel='σ (Å)', ylabel='ε (kcal/mol)')
#print(merged_df_error)
plt.title("Comparing MD and CG RDF's based on the Area ")
plt.savefig(f'peak_area_error_heatmap_{closure}_{functional}.png', dpi=400)
plt.show()








