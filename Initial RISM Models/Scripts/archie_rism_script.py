import os
import shutil
import glob
import subprocess
import time

ROOT_DIR = '/users/ekb16170/rism/'
SUB_DIR = f'{ROOT_DIR}submission_scripts/'
TLEAP_DIR = f'{ROOT_DIR}tleap/diethylether/'
SOLV_DIR = f'{ROOT_DIR}1drism/diethylether/'
INPUT_DIR = f'{ROOT_DIR}diethylether_pdb/'
OUTPUT_DIR = f'{ROOT_DIR}3drism/diethylether/'

closures = ['KH', 'KH,HNC', 'KH,PSE3']
#closures = ['KH']
#--buffer 30 --grdspc 0.3,0.3,0.3 

solvent = 'diethylether'

for closure in closures:
    try:
        os.mkdir(f'{OUTPUT_DIR}{closure}')
    except FileExistsError:
        pass
    
    for pdb_filename in glob.glob(f'{INPUT_DIR}/*.pdb'):
        pdb_name = pdb_filename.split('.pdb')[0].split('/')[-1]
        
        try:
            os.mkdir(f'{OUTPUT_DIR}{closure}/{pdb_name}')
        except FileExistsError:
            pass
        
        try:
            shutil.copyfile(pdb_filename, f'{OUTPUT_DIR}{closure}/{pdb_name}/{pdb_name}.pdb')
            shutil.copyfile(f'{TLEAP_DIR}{pdb_name}/gen.prmtop', f'{OUTPUT_DIR}{closure}/{pdb_name}/gen.prmtop')
            shutil.copyfile(f'{SOLV_DIR}/{solvent}.xvv', f'{OUTPUT_DIR}{closure}/{pdb_name}/{solvent}.xvv')
            shutil.copyfile(f'{SUB_DIR}/3drism_example.sub', f'{OUTPUT_DIR}{closure}/{pdb_name}/{pdb_name}.sub')
        except FileNotFoundError:
            print(f'Cannot find file for {pdb_name}')
            continue
        rism_command = f'rism3d.snglpnt --pdb {pdb_name}.pdb --prmtop gen.prmtop --closure {closure.lower()} --maxstep 50000 --pc+ --gf --guv 3DRISM_{pdb_name} --cuv 3DRISM_{pdb_name} --huv 3DRISM_{pdb_name} --uuv 3DRISM_{pdb_name} --xvv {solvent}.xvv 2>&1 | tee rism3d.log'
        
        with open(f'{OUTPUT_DIR}{closure}/{pdb_name}/{pdb_name}.sub', 'r') as f:
            sub_lines = f.read().splitlines()
        new_lines = []
        
        for line in sub_lines:
            if line.startswith('rism3d'):
                new_lines.append(rism_command)
            else:
                new_lines.append(line)
        
        with open(f'{OUTPUT_DIR}{closure}/{pdb_name}/{pdb_name}.sub', 'w') as f:
            for line in new_lines:
                print(line, file=f)
        cwd = os.getcwd()
        os.chdir(f'{OUTPUT_DIR}{closure}/{pdb_name}')
        subprocess.run(['sbatch', f'{pdb_name}.sub'])
        #time.sleep(10)
        os.chdir(cwd)
        
