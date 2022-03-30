import os
import shutil
import glob
import subprocess
import time

ROOT_DIR = '/users/ekb16170/gaussian/'
SUB_DIR = f'{ROOT_DIR}/'
INPUT_DIR = f'{ROOT_DIR}diethylether/job_submission/'
OUTPUT_DIR = f'{ROOT_DIR}diethylether/job_completion/'

for dir in os.listdir(f'{INPUT_DIR}'):

    try:
        os.mkdir(f'{OUTPUT_DIR}{dir}')
    except FileExistsError:
        pass

    for com_filename in glob.glob(f'{INPUT_DIR}{dir}/*.com'):
	    com_name = com_filename.split('.com')[0].split('/')[-1]

	    try:
	        os.mkdir(f'{OUTPUT_DIR}{dir}/{com_name}')
	    except FileExistsError:
	        pass

	    try:
	        shutil.copyfile(com_filename, f'{OUTPUT_DIR}{dir}/{com_name}/{com_name}.com')
	        shutil.copyfile(f'{SUB_DIR}gaussian_submission.sub', f'{OUTPUT_DIR}{dir}/{com_name}/{com_name}.sub')
	    except FileNotFoundError:
	        print(f'Cannot find file for {com_name}')
	        continue

	    g16_command = f'g16 {com_name}.com'
    
	    with open(f'{OUTPUT_DIR}{dir}/{com_name}/{com_name}.sub', 'r') as f:
	        sub_lines = f.read().splitlines()
	    new_lines = []
    
	    for line in sub_lines:
	        if line.startswith('g16'):
	            new_lines.append(g16_command)
	        else:
	            new_lines.append(line)
    
	    with open(f'{OUTPUT_DIR}{dir}/{com_name}/{com_name}.sub', 'w') as f:
	        for line in new_lines:
	            print(line, file=f)
	    cwd = os.getcwd()
	    os.chdir(f'{OUTPUT_DIR}{dir}/{com_name}')
	    subprocess.run(['sbatch', f'{com_name}.sub'])
	    #time.sleep(72000)
	    os.chdir(cwd)
    
