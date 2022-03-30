import os
import shutil
import glob
import subprocess
import time

ROOT_DIR = '/users/ekb16170/rism/'
INPUT_DIR = f'{ROOT_DIR}diethylether_pdb/'
SUB_DIR = f'{ROOT_DIR}submission_scripts/'
TLEAP_DIR = f'{ROOT_DIR}tleap/diethylether/'

for pdb_filename in glob.glob(f'{INPUT_DIR}*.pdb'):
    #print(pdb_filename)
    pdb_name = pdb_filename.split('.pdb')[0].split('/')[-1]
    #print(pdb_name)
    try:
        os.mkdir(f'{TLEAP_DIR}{pdb_name}')
    except FileExistsError:
        pass
            
    try:
        shutil.copyfile(pdb_filename, f'{TLEAP_DIR}{pdb_name}/{pdb_name}.pdb')
        shutil.copyfile(f'{SUB_DIR}/runleap2.sh', f'{TLEAP_DIR}{pdb_name}/runleap2.sh')
        shutil.copyfile(f'{SUB_DIR}/tleap_example.sub', f'{TLEAP_DIR}{pdb_name}/{pdb_name}.sub')
    except FileNotFoundError:
        print(f'Cannot find file for {pdb_name}')
        continue

    tleap_command = f'antechamber -i {pdb_name}.pdb -fi pdb -o gen.mol2 -fo mol2 -c bcc -s 2 2>&1 | tee antechamber.log'
    with open(f'{TLEAP_DIR}{pdb_name}/{pdb_name}.sub', 'r') as f:
        sub_lines = f.read().splitlines()
    new_lines = []
    for line in sub_lines:
        if line.startswith('antechamber'):
            new_lines.append(tleap_command)
        else:
            new_lines.append(line)
    with open(f'{TLEAP_DIR}{pdb_name}/{pdb_name}.sub', 'w') as f:
        for line in new_lines:
            print(line, file = f)

    cwd = os.getcwd()
    os.chdir(f'{TLEAP_DIR}{pdb_name}')
    subprocess.run(['sbatch', f'{pdb_name}.sub'])
    #time.sleep(1)
    os.chdir(cwd)
       
