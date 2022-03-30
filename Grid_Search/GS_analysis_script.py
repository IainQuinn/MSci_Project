import os
import glob
import pandas as pd
pd.options.mode.chained_assignment = None
import shutil
from sklearn.metrics import mean_squared_error
import csv
import math
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from functools import reduce
from natsort import index_natsorted
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

closures = ['KH,PSE3'] #currently only works for one closure at a time. (need to add loop over analysis)
functional = 'PC+'
molecule = 'diethylether'

end = '_newgridB_tol-12_training'

ROOT_DIR = f'/users/ekb16170/msci_project/rism/3drism/{molecule}/grid_search/{molecule}_combinations/'
EXP_DIR = f'/users/ekb16170/msci_project/rism/exp_data/'
TEMPLATE_DIR = f'/users/ekb16170/msci_project/rism/combinations/diethylether/'

os.chdir(ROOT_DIR)

for closure in closures:

	for combination in os.listdir(f'{ROOT_DIR}{closure}'):
		#print(combination)
		try:
			os.chdir(f'{ROOT_DIR}{closure}/{combination}')
		except NotADirectoryError:
			pass		
		file_names = []
		hfe_values = []
		hfe_gf_values = []
		hfe_pc_values = []
		hfe_uc_values = []
		pmv_values = []

		for mol in os.listdir(f'{ROOT_DIR}{closure}/{combination}'):
			#print(mol)
			for log_path in glob.glob(f'{ROOT_DIR}{closure}/{combination}/{mol}/*.log'):
				with open(f'{log_path}') as log_file:
					lines = log_file.readlines()
				hfe_line = [line for line in lines if line.startswith('rism_excessChemicalPotential')]
				hfe_gf_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialGF')]
				hfe_pc_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialPC')]
				#hfe_uc_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialUC')]
				#pmv_line = [line for line in lines if line.startswith('rism_partialMolarVolume')]

				if hfe_line == []:
					#print(f'Run failed for molecule {mol}')
					hfe_values.append(0)
					hfe_gf_values.append(0)
					hfe_pc_values.append(0)
					#hfe_uc_values.append(0)
					#pmv_values.append(0)
					file_names.append(mol)
				else:
					hfe_values.append(float(hfe_line[0].split()[1]))
					hfe_gf_values.append(float(hfe_gf_line[0].split()[1]))
					hfe_pc_values.append(float(hfe_pc_line[0].split()[1]))
					#hfe_uc_values.append(float(hfe_uc_line[0].split()[1]))
					#pmv_values.append(float(pmv_line[0].split()[1]))
					file_names.append(mol)

		hfe_table = pd.DataFrame([file_names, hfe_values, hfe_gf_values, hfe_pc_values]).transpose()
		hfe_table.columns = ['File', 'dGsolv', 'dGsolv_gf', 'dGsolv_pc']	
		hfe_table.to_csv('results.csv', index=False)

		exp = pd.read_csv(f'{EXP_DIR}exp_{molecule}.csv', usecols=['File', 'dGsolv_exp'])
		calc = pd.read_csv('results.csv', usecols=['File', 'dGsolv', 'dGsolv_gf', 'dGsolv_pc'])
		calc = calc.sort_values(by='File')
		calc = calc.loc[calc.ne(0).all(axis=1)]
		calc.to_csv('results.csv', index=False)

		common = exp.merge(calc,on=['File'])
		common.to_csv('common.csv', index=False)

		try:
			stats = pd.read_csv('common.csv')
			stats['error'] = stats['dGsolv_exp'] - stats['dGsolv']
			stats['error_gf'] = stats['dGsolv_exp'] - stats['dGsolv_gf']
			stats['error_pc+'] = stats['dGsolv_exp'] - stats['dGsolv_pc']
			stats['rmse'] = math.sqrt(mean_squared_error(stats['dGsolv_exp'], stats['dGsolv']))
			stats['rmse_gf'] = math.sqrt(mean_squared_error(stats['dGsolv_exp'], stats['dGsolv_gf']))
			stats['rmse_pc+'] = math.sqrt(mean_squared_error(stats['dGsolv_exp'], stats['dGsolv_pc']))
			stats['bias'] = stats['error'].sum() / stats.shape[0] 
			stats['bias_gf'] = stats['error_gf'].sum() / stats.shape[0]
			stats['bias_pc+'] = stats['error_pc+'].sum() / stats.shape[0] 
			stats['sd'] = stats['error'].std()
			stats['sd_gf'] = stats['error_gf'].std()
			stats['sd_pc+'] = stats['error_pc+'].std()
			stats = stats.round(decimals=2)
			stats['rmse'].iloc[0] = stats['rmse'].iloc[-1]
			stats['rmse'].iloc[1:] = ''
			stats['rmse_gf'].iloc[0] = stats['rmse_gf'].iloc[-1]
			stats['rmse_gf'].iloc[1:] = ''
			stats['rmse_pc+'].iloc[0] = stats['rmse_pc+'].iloc[-1]
			stats['rmse_pc+'].iloc[1:] = ''
			stats['bias'].iloc[0] = stats['bias'].iloc[-1]
			stats['bias'].iloc[1:] = ''
			stats['bias_gf'].iloc[0] = stats['bias_gf'].iloc[-1]
			stats['bias_gf'].iloc[1:] = ''
			stats['bias_pc+'].iloc[0] = stats['bias_pc+'].iloc[-1]
			stats['bias_pc+'].iloc[1:] = ''
			stats['sd'].iloc[0] = stats['sd'].iloc[-1]
			stats['sd'].iloc[1:] = ''
			stats['sd_gf'].iloc[0] = stats['sd_gf'].iloc[-1]
			stats['sd_gf'].iloc[1:] = ''
			stats['sd_pc+'].iloc[0] = stats['sd_pc+'].iloc[-1]
			stats['sd_pc+'].iloc[1:] = ''

			plot1 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv', label=f'{closure}', color='r')
			plot2 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv_gf', label='GF', color='g', ax=plot1)
			plot3 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv_pc', label='PC+', color='b', ax=plot1)
			plt.savefig('stats_plot.png')
			plt.close()

			print(f'{combination}', 'rmse', stats.iloc[0, 8], 'rmse_gf', stats.iloc[0, 9], 'rmse_pc+', stats.iloc[0, 10])
			with open('stats_file.txt', 'w') as f:
				f.write(f'{combination}' + '\n'  + 'number of molecules that successfully ran = ' + str(stats.shape[0]) + ' / ' + str(exp.shape[0]) + '\n' + f'rmse_{closure} = ' + str(stats.iloc[0, 8]) + '\n' + 'rmse_gf = ' + str(stats.iloc[0, 9]) + '\n' + 'rmse_pc+ = ' + str(stats.iloc[0, 10]) + '\n' + f'bias_{closure} = ' + str(stats.iloc[0, 11]) + '\n' + 'bias_gf = ' + str(stats.iloc[0, 12]) + '\n' + 'bias_pc+ = ' + str(stats.iloc[0, 13]) + '\n' + f'sd_{closure} = ' + str(stats.iloc[0, 14]) + '\n' + 'sd_gf = ' + str(stats.iloc[0, 15]) + '\n' + 'sd_pc+ = ' + str(stats.iloc[0, 16]) + '\n\n')

		except ValueError:
			pass
	
		os.remove('results.csv')
		os.remove('common.csv')
		stats.to_csv('results_stats.csv', index=False)

os.chdir(f'{ROOT_DIR}')

data_combinations_complete = []
data_combinations_full = []
data_pc_rmse = []
data_closure_rmse = []
data_gf_rmse = []
data_pc_bias = []
data_closure_bias = []
data_gf_bias = []
data_pc_sd = []
data_closure_sd = []
data_gf_sd = []
data_number = []
data_eps = []
data_rmin_half = []

for closure in closures:

	read_files = glob.glob(f'{ROOT_DIR}{closure}/*/*.txt')

	with open(f'{closure}_{functional}_stats_summary.txt', 'wb') as outfile:
		for f in read_files:
			with open(f, 'rb') as infile:
				outfile.write(infile.read())

	with open(f'{closure}_{functional}_stats_summary.txt', 'r') as f:
		filedata = f.readlines()
	#	print(filedata)
		
		for line in filedata:
			if f'{molecule}' in line:
				combination = line.split()[0]
				data_combinations_complete.append(combination)
#				print(combination)

			elif f'rmse_{closure}' in line:
				rmse = line.split()[2]
				data_closure_rmse.append(rmse)
#				print(rmse)

			elif 'rmse_gf' in line:
				rmse_gf = line.split()[2]
				data_gf_rmse.append(rmse_gf)
#				print(rmse_gf)

			elif 'rmse_pc+' in line:
				rmse_pc = line.split()[2]
				data_pc_rmse.append(rmse_pc)
#				print(rmse_pc)

			elif 'number' in line:
				number = line.split()[7]
				data_number.append(number)
#				print(number)

			elif f'bias_{closure}' in line:
				bias = line.split()[2]
				data_closure_bias.append(bias)
#				print(bias)

			elif 'bias_gf' in line:
				bias_gf = line.split()[2]
				data_gf_bias.append(bias_gf)
#				print(bias_gf)

			elif 'bias_pc+' in line:
				bias_pc = line.split()[2]
				data_pc_bias.append(bias_pc)
#				print(bias_pc)

			elif f'sd_{closure}' in line:
				sd = line.split()[2]
				data_closure_sd.append(sd)
#				print(sd)

			elif 'sd_gf' in line:
				sd_gf = line.split()[2]
				data_gf_sd.append(sd_gf)
#				print(sd_gf)

			elif 'sd_pc+' in line:
				sd_pc = line.split()[2]
				data_pc_sd.append(sd_pc)
#				print(sd_pc)

df_combinations_complete = pd.DataFrame(data_combinations_complete, columns=['Combinations'])
#print(df_combinations)
df_rmse_closure = pd.DataFrame(data_closure_rmse, columns=[f'RMSE {closure}'])
#print(df_rmse_closure)
df_rmse_gf = pd.DataFrame(data_gf_rmse, columns=['RMSE GF'])
#print(df_rmse_gf)
df_rmse_pc = pd.DataFrame(data_pc_rmse, columns=['RMSE PC+'])
#print(df_rmse_pc)
df_bias_closure = pd.DataFrame(data_closure_bias, columns=[f'Bias {closure}'])
#print(df_bias_closure)
df_bias_gf = pd.DataFrame(data_gf_bias, columns=['Bias GF'])
#print(df_bias_gf)
df_bias_pc = pd.DataFrame(data_pc_bias, columns=['Bias PC+'])
#print(df_bias_pc)
df_sd_closure = pd.DataFrame(data_closure_sd, columns=[f'SD {closure}'])
#print(df_sd_closure)
df_sd_gf = pd.DataFrame(data_gf_sd, columns=['SD GF'])
#print(df_sd_gf)
df_sd_pc = pd.DataFrame(data_pc_sd, columns=['SD PC+'])
#print(df_sd_pc)
df_number = pd.DataFrame(data_number, columns=['No. of molecules that ran'])
#print(df_number)
df_analysis = pd.concat([df_combinations_complete, df_rmse_closure, df_rmse_gf, df_rmse_pc, df_bias_closure, df_bias_gf, df_bias_pc, df_sd_closure, df_sd_gf, df_sd_pc, df_number], axis=1)
#print(df_analysis)
#df_analysis.to_csv('test.csv', index=False)

for combinations in os.listdir(f'{TEMPLATE_DIR}'):
	
	data_combinations_full.append(f'{combinations}')

	for mdl in glob.glob(f'{TEMPLATE_DIR}{combinations}/*.mdl'):
		with open(f'{mdl}') as mdl_file:
			lines = mdl_file.readlines()
			lines = [i.replace('\n','') for i in lines]
			lines = [i.replace('  ','') for i in lines]
#			print(lines)
		for i, line in enumerate(lines):
			if 20 < i < 22:
				eps = lines[i]
				data_eps.append(eps)
#				print(data_eps)

			elif 23 < i < 25:
				rmin_half = lines[i]
				data_rmin_half.append(rmin_half)
#				print(lines[i])

df_combinations_full = pd.DataFrame(data_combinations_full, columns=['Combinations'])
#print(df_combinations_full)
df_eps = pd.DataFrame(data_eps, columns=['eps'])
#print(df_eps)
df_rmin_half = pd.DataFrame(data_rmin_half, columns=['rmin/2'])
#print(df_rmin_half)
df_sigma = pd.DataFrame(data_rmin_half, columns=['sigma'])
df_sigma = df_sigma.astype(float)
df_sigma = df_sigma['sigma'] * 0.89 * 2
#print(df_sigma)
df_full = pd.concat([df_combinations_full, df_eps, df_rmin_half, df_sigma], axis=1)
#print(df_full)

df = reduce(lambda x,y: pd.merge(x,y, on='Combinations', how='outer'), [df_analysis, df_full])
df = df.sort_values(by='Combinations', key=lambda x: np.argsort(index_natsorted(x)))
df_drop = df.dropna(subset=[f'RMSE {closure}', 'RMSE GF', 'RMSE PC+', 'No. of molecules that ran'])
#print(df)
#print(df_drop)

df.to_csv(f'{closure}_{functional}.csv', index=False)


df = df.replace(np.nan, '0', regex=True)
df['No. of molecules that ran'] = df['No. of molecules that ran'].astype(float)
df.loc[df['No. of molecules that ran'] < 10, [f'RMSE {functional}']] = 'NaN' #remove results with fewer than x molecules that ran, change to 1/10 of solute dataset
df.loc[df[f'RMSE {functional}'] == 'NaN', ['No. of molecules that ran']] = 'NaN'
#print(df)

#df = df.sort_values(by=['sigma'])
#n = 40
#df = df.drop(df.tail(n).index)
#df = df.sort_values(by='Combinations', key=lambda x: np.argsort(index_natsorted(x)))

df_number = df[['eps', 'sigma', f'RMSE {functional}']].copy()
df_number['eps'] = df_number['eps'].apply(lambda x: float(x))
df_number['sigma'] = df_number['sigma'].apply(lambda x: float(x)) 
df_number['sigma'] = df_number['sigma'].round(2)
df_number[f'RMSE {functional}'] = df_number[f'RMSE {functional}'].apply(lambda x: float(x))
df_number = df_number.pivot(index='eps', columns='sigma', values=f'RMSE {functional}')
fig, ax = plt.subplots(figsize=(12, 12))
ax = sns.heatmap(df_number, cbar=False, annot=True, annot_kws={'color': 'white'}, vmin=0, vmax=4.5)

df_error = df[['eps', 'sigma', f'RMSE {functional}']].copy()
df_error['eps'] = df_error['eps'].apply(lambda x: float(x))
df_error['eps'] = df_error['eps'].round(2)
df_error['sigma'] = df_error['sigma'].apply(lambda x: float(x)) 
df_error['sigma'] = df_error['sigma'].round(2)
df_error[f'RMSE {functional}'] = df_error[f'RMSE {functional}'].apply(lambda x: float(x))
df_error = df_error.pivot(index='eps', columns='sigma', values=f'RMSE {functional}')
ax2 = sns.heatmap(df_error, cbar_kws={'label': f'RMSE (kcal/mol)'}, vmin=0, vmax=4.5) #change label when looping over each closure
ax2.set(xlabel='σ (Å)', ylabel='ε (kcal/mol)')
#print(df_error)
plt.title(f"{functional} Functional SFE Heatmap")
plt.savefig(f'{closure}_{functional}_heatmap_training_cut_lim.png', dpi=1000) #change name as needed
plt.show()
