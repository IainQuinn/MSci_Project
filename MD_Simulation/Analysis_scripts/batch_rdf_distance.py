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

molecule = 'diethylether'
closure = 'KH,HNC'
functional = 'PC+'

ROOT_DIR = f'/users/ekb16170/msci_project/rism/combinations/diethylether/'
RDF_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/diethylether_iain_done/'
SAVE_DIR = f'/users/ekb16170/msci_project/Gromacs/results_analysis/save_dir/distance/'
D_DIR = f'/users/ekb16170/msci_project/rism/3drism/diethylether/grid_search/diethylether_combinations/Results/{closure}_Results/'

#gvvs = glob.glob(f'{ROOT_DIR}/*/chloroform.gvv')

os.chdir(SAVE_DIR)

mdl_name_list = []
max_val_list = []
rel_dis_list = []

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
			
				max_val = max(sorted_data['g(r)'])
				max_val_list.append(float(max_val))

				rel_dis_row = sorted_data['g(r)'].argmax()
				rel_dis = sorted_data['Distance(Å)'].iloc[rel_dis_row]
				#print(rel_dis)
				rel_dis_list.append(float(rel_dis))

			else:
				max_val_list.append(float('NaN'))
				rel_dis_list.append(float('NaN'))

		except FileNotFoundError:
			continue

#print(mdl_name_list)
#print(max_val_list)
#print(rel_dis_list)

mdl_dict = {'Combinations':mdl_name_list, 'mdl_max_energy':max_val_list, 'mdl_rel_distance':rel_dis_list}
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

mdl_df = mdl_df.sort_values(by=['Combinations'])
#print(mdl_df)

df = pd.read_csv(f'{D_DIR}{closure}_{functional}.csv')
df = df.sort_values(by=['Combinations'])
df = df.replace(np.nan, '0', regex=True)
df['No. of molecules that ran'] = df['No. of molecules that ran'].astype(float)
df.loc[df['No. of molecules that ran'] < 10, [f'RMSE {functional}']] = 'NaN' #remove results with fewer than x molecules that ran
df.loc[df[f'RMSE {functional}'] == 'NaN', ['No. of molecules that ran']] = 'NaN'
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

merged_df_number = merged_df[['eps', 'sigma', 'distance_dif']].copy()
merged_df_number['eps'] = merged_df_number['eps'].apply(lambda x: float(x))
merged_df_number['sigma'] = merged_df_number['sigma'].apply(lambda x: float(x)) 
merged_df_number['sigma'] = merged_df_number['sigma'].round(2)
merged_df_number['distance_dif'] = merged_df_number['distance_dif'].apply(lambda x: float(x))
merged_df_number = merged_df_number.pivot(index='eps', columns='sigma', values='distance_dif')
#fig, ax = plt.subplots(figsize=(12, 12))
ax = sns.heatmap(merged_df_number, cbar=False, annot=True, annot_kws={'color': 'white'}, cmap="mako", fmt='.1g')

merged_df_error = merged_df[['eps', 'sigma', 'distance_dif']].copy()
merged_df_error['eps'] = merged_df_error['eps'].apply(lambda x: float(x))
merged_df_error['eps'] = merged_df_error['eps'].round(2)
merged_df_error['sigma'] = merged_df_error['sigma'].apply(lambda x: float(x)) 
merged_df_error['sigma'] = merged_df_error['sigma'].round(2)
merged_df_error['distance_dif'] = merged_df_error['distance_dif'].apply(lambda x: float(x))
merged_df_error = merged_df_error.pivot(index='eps', columns='sigma', values='distance_dif')
ax2 = sns.heatmap(merged_df_error, cbar_kws={'label': f'1st Solvation Shell Peak Position Error'}, cmap="mako", vmin=-0.5, vmax=2.0, fmt='.1g')
ax2.set(xlabel='σ (Å)', ylabel='ε (kcal/mol)')
#print(merged_df_error)
plt.title("Comparison of MD and CG RDF's based on the Position")
plt.savefig(f'peak_position_error_heatmap.png', dpi=400)
plt.show()

merged_df_number = merged_df[['eps', 'sigma', 'energy_dif']].copy()
merged_df_number['eps'] = merged_df_number['eps'].apply(lambda x: float(x))
merged_df_number['sigma'] = merged_df_number['sigma'].apply(lambda x: float(x)) 
merged_df_number['sigma'] = merged_df_number['sigma'].round(2)
merged_df_number['energy_dif'] = merged_df_number['energy_dif'].apply(lambda x: float(x))
merged_df_number = merged_df_number.pivot(index='eps', columns='sigma', values='energy_dif')
#fig, ax = plt.subplots(figsize=(12, 12))
ax = sns.heatmap(merged_df_number, cbar=False, annot=True, annot_kws={'color': 'white'}, cmap="crest", fmt='.1g')

merged_df_error = merged_df[['eps', 'sigma', 'energy_dif']].copy()
merged_df_error['eps'] = merged_df_error['eps'].apply(lambda x: float(x))
merged_df_error['eps'] = merged_df_error['eps'].round(2)
merged_df_error['sigma'] = merged_df_error['sigma'].apply(lambda x: float(x)) 
merged_df_error['sigma'] = merged_df_error['sigma'].round(2)
merged_df_error['energy_dif'] = merged_df_error['energy_dif'].apply(lambda x: float(x))
merged_df_error = merged_df_error.pivot(index='eps', columns='sigma', values='energy_dif')
ax2 = sns.heatmap(merged_df_error, cbar_kws={'label': f'1st Solvation Shell Peak Height Error'}, cmap="crest", vmin=-2.5, vmax=0, fmt='.1g')
ax2.set(xlabel='σ (Å)', ylabel='ε (kcal/mol)')
#print(merged_df_error)
plt.title("Comparison of MD and CG RDF's based on the Height")
plt.savefig(f'peak_height_error_heatmap.png', dpi=400)
plt.show()

