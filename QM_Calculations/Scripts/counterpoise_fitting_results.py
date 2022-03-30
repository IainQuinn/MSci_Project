import os
import glob
import pandas as pd
import shutil
import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from natsort import index_natsorted

config = 'G'

colour = 'black'

ROOT_DIR = f'/users/ekb16170/gaussian/diethylether/job_completion/dimer_G/'

os.chdir(ROOT_DIR)

file_names = []
complexation_values = []
centre_mol = []


for dir in os.listdir(f'{ROOT_DIR}'):
	#print(dir)

	for subdir in os.listdir(f'{ROOT_DIR}{dir}'):

		for log_path in glob.glob(f'{ROOT_DIR}{dir}/*.log'):
			with open(f'{log_path}') as log_file:		
				lines = log_file.readlines()
	
	check_line = [line for line in lines if line.startswith(' Counterpoise corrected energy =')]
	complexation_values_line = [line for line in lines if line.startswith('           complexation energy =')]
	#print(complexation_values_line)

	if check_line == []:
		print(f'Run failed for molecule {dir}')
		complexation_values.append(0)

	else:
		complexation_values.append(float(complexation_values_line[-1].split()[3]))
		file_names.append(dir)


	scf_table = pd.DataFrame([file_names, complexation_values]).transpose()
	scf_table.columns = ['File', 'complexation_energy']
	scf_table.to_csv('results.csv', index=False)

data = pd.read_csv('results.csv')
sorted_data = data.sort_values(by='File', key=lambda x: np.argsort(index_natsorted(x)))
sorted_data.to_csv('results.csv', index=False)
sorted_data = pd.read_csv('results.csv')
distance_1 = 4.85
distance_2 = 14.22
distance_list = np.arange(distance_1, distance_2, (distance_2 - distance_1)/101).tolist() #change distances from results.csv for each dimer
sorted_data['Distance'] = distance_list
column_titles = ['Distance', 'complexation_energy', 'File']
sorted_data = sorted_data.reindex(columns=column_titles)
sorted_data.to_csv('results.csv', index=False)
sorted_data_focused = sorted_data.iloc[1:90] #ignore extremes of wave for function 
plt.plot(sorted_data_focused['Distance'], sorted_data_focused['complexation_energy'], color=f'{colour}')
plt.title(f'Dimer Configuration {config} Interaction Energy') 
plt.xlabel('Distance (Å)')
plt.ylabel('Energy (kcal/mol)')
plt.xlim(int(distance_1 - 1), int(distance_2 - 2))
plt.ylim(-3, 4)
plt.xticks(np.arange(int(distance_1)-1, int(distance_2), 1))
plt.yticks(np.arange(-3, 5, 1))
plt.savefig(f'cp_curve_{config}.png', dpi=1000)
plt.show()

def func(distance, a, b):
	return (4 * a * ((b/distance)**12 - (b/distance)**6))

#sorted_data_well = sorted_data.iloc[2:25] #ignore extremes of wave for function 
popt, pcov = curve_fit(func, sorted_data_focused['Distance'], sorted_data_focused['complexation_energy'], p0=[1.50, 10.00], maxfev=1000000)

print('sigma'), print(popt[1])
sigma = str(round(popt[1],2))
epsilon = str(round(popt[0],2))
print('epsilon'), print(popt[0])
with open('parameter_file.txt', 'w') as f:
	f.write('epsilon = ' + str(popt[0]) + '\n' + 'sigma = ' + str(popt[1]))

plt.plot(sorted_data_focused['Distance'], sorted_data_focused['complexation_energy'], label=f'Dimer {config} Interaction Energy', color=f'{colour}')
plt.plot(sorted_data_focused['Distance'], func(sorted_data_focused['Distance'], popt[0], popt[1]), label='LJ Fitted function', color='orange')
plt.legend(loc='best')
plt.title(f'Dimer Configuration {config} Potential vs. LJ Fitted Function')
plt.xlabel('Distance (Å)')
plt.ylabel('Energy (kcal/mol)')
plt.ylabel('Energy (kcal/mol)')
plt.xlim(int(distance_1 - 1), int(distance_2 - 2))
plt.ylim(-3, 4)
plt.xticks(np.arange(int(distance_1)-1, int(distance_2), 1))
plt.yticks(np.arange(-3, 5, 1))
plt.text(8.00, 2.60, 'σ = ' + sigma + ' Å', ha='left', fontsize=12)
plt.text(8.00, 2.30, 'ε = ' + epsilon + ' kcal/mol', ha='left', fontsize=12)
plt.savefig(f'curve_fitting_{config}.png', dpi=1000)
plt.show()

#x = np.arange(3.02, 11.38, 0.083)
#lj = 4 * popt[0] * ((popt[1]/x)**12 - (popt[1]/x)**6)
#plt.plot(sorted_data['Distance'], sorted_data['complexation_energy'], label=f'Dimer {config} Interaction Energy', color=f'{colour}')
#plt.plot(x, lj, label='LJ Fitted function', color='orange')
#plt.legend(loc='best')
#plt.title(f'Dimer Configuration {config} Potential vs. LJ Fitted Function')
#plt.xlabel('Distance (Å)')
#plt.ylabel('Energy (kcal/mol)')
#plt.xlim(2, 10)
#plt.ylim(-2, 4)
#plt.xticks(np.arange(3.3, 5, 1))
#plt.yticks(np.arange(-1, 5, 1))
#plt.text(9.70, 2.80, 'σ = ' + sigma, ha='center', fontsize=12)
#plt.text(9.70, 2.50, 'ε = ' + epsilon, ha='center', fontsize=12)
#plt.savefig(f'curve_fitting_extended_{config}.png', dpi=1000)
#plt.show()





