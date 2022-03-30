import os
import glob
import pandas as pd
pd.options.mode.chained_assignment = None
import shutil
from sklearn.metrics import mean_squared_error
import csv
import math
import matplotlib.pyplot as plt
import seaborn as sns

ROOT_DIR = '/users/ekb16170/msci_project/rism/3drism/diethylether/grid_search/diethylether_combinations/KH,PSE3/'
EXP_DIR = '/users/ekb16170/msci_project/rism/exp_data/'
RES_DIR = '/users/ekb16170/msci_project/rism/3drism/diethylether/grid_search/diethylether_combinations/'

closures = 'diethylether_90'

os.chdir(ROOT_DIR)

#for closure in closures:
#	os.chdir(f'{ROOT_DIR}{closure}')
#	print(closure)
file_names = []
hfe_values = []
hfe_gf_values = []
hfe_pc_values = []
hfe_uc_values = []
pmv_values = []
failed_mols = []

for mol in os.listdir(f'{ROOT_DIR}{closures}'):
	print(mol)
	for log_path in glob.glob(f'{ROOT_DIR}{closures}/{mol}/*.log'):
		with open(f'{log_path}') as log_file:
			lines = log_file.readlines()
		hfe_line = [line for line in lines if line.startswith('rism_excessChemicalPotential')]
		hfe_gf_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialGF')]
		hfe_pc_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialPC')]
			#hfe_uc_line = [line for line in lines if line.startswith('rism_excessChemicalPotentialUC')]
			#pmv_line = [line for line in lines if line.startswith('rism_partialMolarVolume')]

		if hfe_line == []:
			print(f'Run failed for molecule {mol}')
			failed_mols.append(mol)
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
hfe_table.to_csv(f'{RES_DIR}results.csv', index=False)

exp = pd.read_csv(f'{EXP_DIR}exp_diethylether.csv', usecols=['File', 'dGsolv_exp'])
calc = pd.read_csv(f'{RES_DIR}results.csv', usecols=['File', 'dGsolv', 'dGsolv_gf', 'dGsolv_pc'])
max_norm = calc.loc[calc['dGsolv'].idxmax()]
max_gf = calc.loc[calc['dGsolv_gf'].idxmax()]
max_pc = calc.loc[calc['dGsolv_pc'].idxmax()]
calc = calc.sort_values(by='File')
calc = calc.loc[calc.ne(0).all(axis=1)]
calc.to_csv(f'{RES_DIR}results.csv', index=False)

common = exp.merge(calc,on=['File'])
common.to_csv(f'{RES_DIR}common.csv', index=False)

stats = pd.read_csv(f'{RES_DIR}common.csv')
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

#Plotting closure free energy functional ---------------------------------------------------

g1 = sns.regplot(data=stats, x='dGsolv_exp', y='dGsolv', scatter_kws={"color": "blue"})
g1.set(xlabel='ΔG$_{solv}^{exp}$ (kcal/mol)', ylabel='ΔG$_{solv}^{calc}$ KH (kcal/mol)')
#plt.text(-17, 125.0, 'RMSE = ' + str(stats.iloc[0, 8]), ha='left', fontsize=12)
#plt.text(-17, 115.0, 'Bias = ' + str(stats.iloc[0, 11]), ha='left', fontsize=12)
#plt.text(-17, 105.0, 'SD = ' + str(stats.iloc[0, 14]), ha='left', fontsize=12)
plt.title(f'{closures} Free Energy Functional Vs Experimental Data')
plt.savefig(f'{RES_DIR}{closures}_correlation.png', dpi=1000)
plt.show()

#Plotting GF free energy functional --------------------------------------------------------

g1 = sns.regplot(data=stats, x='dGsolv_exp', y='dGsolv_gf', scatter_kws={"color": "green"})
g1.set(xlabel='ΔG$_{solv}^{exp}$ (kcal/mol)', ylabel='ΔG$_{solv}^{calc}$ GF (kcal/mol)')
#plt.text(-17, 125.0, 'RMSE = ' + str(stats.iloc[0, 9]), ha='left', fontsize=12)
#plt.text(-17, 115.0, 'Bias = ' + str(stats.iloc[0, 12]), ha='left', fontsize=12)
#plt.text(-17, 105.0, 'SD = ' + str(stats.iloc[0, 15]), ha='left', fontsize=12)
plt.title('GF Free Energy Functional Vs Experimental Data')
plt.savefig(f'{RES_DIR}GF_correlation.png', dpi=1000)
plt.show()

#Plotting PC+ free energy functional --------------------------------------------------------

g1 = sns.regplot(data=stats, x='dGsolv_exp', y='dGsolv_pc', scatter_kws={"color": "red"})
g1.set(xlabel='ΔG$_{solv}^{exp}$ (kcal/mol)', ylabel='ΔG$_{solv}^{calc}$ PC+ (kcal/mol)')
#plt.text(-17, 125.0, 'RMSE = ' + str(stats.iloc[0, 10]), ha='left', fontsize=12)
#plt.text(-17, 115.0, 'Bias = ' + str(stats.iloc[0, 13]), ha='left', fontsize=12)
#plt.text(-17, 105.0, 'SD = ' + str(stats.iloc[0, 16]), ha='left', fontsize=12)
plt.title('PC+ Free Energy Functional Vs Experimental Data')
plt.savefig(f'{RES_DIR}PC_correlation.png', dpi=1000)
plt.show()

#Plotting all three together -----------------------------------------------------------------

plot1 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv', label=f'{closures}', color='b')
plot2 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv_gf', label='GF', color='g', ax=plot1)
plot3 = stats.plot(kind='scatter', x='dGsolv_exp', y='dGsolv_pc', label='PC+', color='r', ax=plot1)
#plt.text(-18, 175.0, 'KH RMSE = ' + str(stats.iloc[0, 8]), ha='left', fontsize=12)
#plt.text(-18, 160.0, 'GF RMSE = ' + str(stats.iloc[0, 9]), ha='left', fontsize=12)
#plt.text(-18, 145.0, 'PC+ RMSE = ' + str(stats.iloc[0, 10]), ha='left', fontsize=12)
plt.xlabel('ΔG$_{solv}^{exp}$ (kcal/mol)')
plt.ylabel('ΔG$_{solv}^{calc}$ KH (kcal/mol)')
plt.title(f'{closures}, GF & PC+  Free Energy Functionals Vs Experimental Data')
plt.savefig(f'{RES_DIR}stats_plot_{closures}.png', dpi=1000)

print(os.getcwd())
print('rmse', stats.iloc[0, 8])
print('rmse_gf', stats.iloc[0, 9])
print('rmse_pc+', stats.iloc[0, 10])
print('bias', stats.iloc[0, 11])
print('bias_gf', stats.iloc[0, 12])
print('bias_pc+', stats.iloc[0, 13])
print('sd', stats.iloc[0, 14])
print('sd_gf', stats.iloc[0, 15])
print('sd_pc+', stats.iloc[0, 16])
with open(f'{RES_DIR}stats_file_{closures}.txt', 'w') as f:
	f.write(f'rmse_{closures} = ' + str(stats.iloc[0, 8]) + '\n' + 'rmse_gf = ' + str(stats.iloc[0, 9]) + '\n' + 'rmse_pc+ = ' + str(stats.iloc[0, 10]) + '\n' + 'bias = '+ str(stats.iloc[0, 11]) + '\n' + 'bias_gf = ' + str(stats.iloc[0, 12]) +'\n' +  'bias_pc+ = ' + str(stats.iloc[0, 13]) + '\n' + 'sd = ' + str(stats.iloc[0, 14]) + '\n' + 'sd_gf = '+ str(stats.iloc[0, 15]) + '\n' +'sd_pc+ = ' + str(stats.iloc[0, 16]))
	
with open(f'{RES_DIR}failed_mols.txt', 'w') as f:
	f.writelines(["%s\n" % item  for item in failed_mols])
f.close()

print(max_norm, max_gf, max_pc)

os.remove(f'{RES_DIR}results.csv')
os.remove(f'{RES_DIR}common.csv')
stats.to_csv(f'{RES_DIR}results_stats_{closures}.csv', index=False)

#exp = pd.read_csv(f'results_stats_{closures}.csv', usecols=['dGsolv_exp', 'dGsolv_pc'])
#g1 = sns.regplot(data=exp, x='dGsolv_exp', y='dGsolv_pc')
#g1.set(xlabel='ΔG$_{solv}^{exp}$ (kcal/mol)', ylabel='ΔG$_{solv}^{calc}$ PSE3 PC+ (kcal/mol)')
#plt.text(-3.6, -10.4, 'RMSE = 1.91', ha='center', fontsize=12)
#plt.text(-3.6, -11.2, 'Bias = -1.59', ha='center', fontsize=12)
#plt.text(-3.6, -12, 'SD = 1.06', ha='center', fontsize=12)
#plt.savefig('test_KH_exp.png', dpi=1000)
#plt.show()
