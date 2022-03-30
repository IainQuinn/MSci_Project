import os
import os.path
import glob
import pandas as pd
pd.set_option('display.float_format', '{:.2E}'.format)
from itertools import product
import numpy as np
import shutil
import csv
import subprocess
import time

maksim_eps = 1.00000000E-02 #shallowest minima, C
maksim_sigma = 1.92134831E+00 #actually rmin/2(/0.89/2) shortest distance, D

new_eps = 3.71000000E+00 #deepest minima, B
new_sigma = 4.09550562E+00 #actually rmin/2(/0.89/2) longest distance, C

molecule = 'diethylether' #all variables dependent on this. Change with each molecule.

dataset = 'diethylether_pdb' #change dataset for specific molecule

mdl_file = f'{molecule}.mdl' 

sh_file = f'{molecule}.sh'

csv_file = f'{molecule}_combinations.csv'

xvv_file = f'{molecule}.xvv'

closures = ['KH', 'KH,HNC', 'KH,PSE3']
#closures = ['KH', 'KH,PSE3']

end = ''

ROOT_DIR = '/users/ekb16170/msci_project/rism/combinations/'
TEMPLATE_DIR = '/users/ekb16170/msci_project/rism/combinations/template/'
CALC_DIR = f'/users/ekb16170/msci_project/rism/3drism/{molecule}/grid_search/'
INPUT_DIR = f'/users/ekb16170/msci_project/rism/{dataset}/'
SUB_DIR = '/users/ekb16170/msci_project/rism/submission_scripts/'
TLEAP_DIR = f'/users/ekb16170/msci_project/rism/tleap/{molecule}/'

os.chdir(ROOT_DIR)

os.mkdir(f'{molecule}')

eps_array = np.linspace(maksim_eps, new_eps, 10)
#print(eps_array)

sigma_array = np.linspace(maksim_sigma, new_sigma, 10)
#print(sigma_array)

parameters = pd.DataFrame({'eps' : eps_array, 'sigma' : sigma_array})
parameters = parameters.round(8)
parameters.set_index('eps', inplace=True)
#print(parameters)

combinations = pd.DataFrame(list(product(eps_array, sigma_array)), columns=['eps', 'sigma'])
combinations = combinations.round(8)
combinations.set_index('eps', inplace=True)
combinations.to_csv(f'{csv_file}')
shutil.copy(f'{csv_file}', f'{TEMPLATE_DIR}') 
os.remove(f'{csv_file}')
#print(combinations)
#print(combinations.shape[0])

new_parameters = pd.read_csv(f'{TEMPLATE_DIR}{csv_file}')
#print(new_parameters)

shutil.copy(f'{TEMPLATE_DIR}{mdl_file}', f'{ROOT_DIR}')

for mdl in glob.glob(f'{ROOT_DIR}*.mdl'):
    with open(mdl, 'r') as f:
        filedata = f.readlines()

        for i, row in new_parameters.iterrows():
            new_filedata = []
            for line in filedata:
                if 'replace1' in line:
                    new_filedata.append(line.replace('replace1', '{:.8e}'.format(row.eps)))
                elif 'replace2' in line:
                    new_filedata.append(line.replace('replace2', '{:.8e}'.format(row.sigma)))
                else:
                    new_filedata.append(line)

            new_file = mdl.replace('.mdl', f'_{i}.mdl')
            with open(new_file, 'w+') as g:
                for line in new_filedata:
                    print(line.rstrip(), file=g)

os.remove(mdl_file)

for mdl in glob.glob(f'{ROOT_DIR}*.mdl'):
    mdl_filename = mdl.split('.mdl')[0].split('/')[-1]

    try:
        os.mkdir(f'{ROOT_DIR}{molecule}/{mdl_filename}')
    except FileExistsError:
        pass

    shutil.move(mdl, f'{ROOT_DIR}{molecule}/{mdl_filename}/')

    for sh in glob.glob(f'{TEMPLATE_DIR}{sh_file}'):

        shutil.copyfile(f'{TEMPLATE_DIR}{sh_file}', f'{ROOT_DIR}{molecule}/{mdl_filename}/{sh_file}')
		
        with open(f'{ROOT_DIR}{molecule}/{mdl_filename}/{sh_file}', 'r') as f:
            filedata = f.read()
	
        filedata = filedata.replace('edit', f'{mdl_filename}')

        with open(f'{ROOT_DIR}{molecule}/{mdl_filename}/{sh_file}', 'w') as f:
            f.write(filedata)

    cwd = os.getcwd()
    os.chdir(f'{ROOT_DIR}{molecule}/{mdl_filename}')
    subprocess.run('ls')
    subprocess.run(f'sh {sh_file} &', shell=True)
    os.chdir(cwd)
    
time.sleep(60)
os.mkdir(f'{CALC_DIR}{molecule}_combinations{end}')

for closure in closures:
    try:
        os.mkdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}')
    except FileExistsError:
        pass
    
    for mol in os.listdir(f'{ROOT_DIR}{molecule}'):
#	    print(mol)

        if os.path.exists(f'{ROOT_DIR}{molecule}/{mol}/{xvv_file}'):
#           print(f'{mol}'), print('xvv exists')
            os.mkdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}')

for closure in closures:

    for mol in os.listdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}'):

        try:
            shutil.copyfile(f'{SUB_DIR}/3drism_batch_test.sub', f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/3drism_batch_test.sub')
        except FileExistsError:
            pass

        rism_command = f'	rism3d.snglpnt --pdb $i.pdb --prmtop gen.prmtop --closure {closure.lower()} --maxstep 10000 --pc+ --gf --guv 3DRISM_$i --cuv 3DRISM_$i --huv 3DRISM_$i --uuv 3DRISM_$i --xvv {xvv_file} 2>&1 | tee rism3d.log '
        
        with open(f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/3drism_batch_test.sub', 'r') as f:
            sub_lines = f.read().splitlines()
        new_lines = []
        
        for line in sub_lines:
            if line.startswith('	rism3d'):
                new_lines.append(rism_command)
            else:
                new_lines.append(line)
          
        with open(f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/3drism_batch_test.sub', 'w') as f:
            for line in new_lines:
                print(line, file=f)

        for pdb_filename in glob.glob(f'{INPUT_DIR}/*.pdb'):
            pdb_name = pdb_filename.split('.pdb')[0].split('/')[-1]
        
            try:
                os.mkdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/{pdb_name}')
            except FileExistsError:
                pass

            try:
                shutil.copyfile(f'{ROOT_DIR}{molecule}/{mol}/{xvv_file}', f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/{pdb_name}/{xvv_file}')
                shutil.copyfile(f'{TLEAP_DIR}{pdb_name}/gen.prmtop', f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/{pdb_name}/gen.prmtop')
                shutil.copyfile(f'{TLEAP_DIR}{pdb_name}/{pdb_name}.pdb', f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}/{pdb_name}/{pdb_name}.pdb')
                
            except FileNotFoundError:
                print(f'Cannot find file for {pdb_name}')
                continue

for closure in closures:

    for mol in os.listdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}'):

        cwd = os.getcwd()
        os.chdir(f'{CALC_DIR}{molecule}_combinations{end}/{closure}/{mol}')
        #print(pdb)
        subprocess.run(['sbatch', '3drism_batch_test.sub'])
        #time.sleep(30)
        os.chdir(cwd)
  
