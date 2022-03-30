import os
import shutil
import glob
import subprocess
import time
import pandas as pd
import re
import numpy as np
import subprocess

tol_ls = []
root_dir = "/users/ekb16170/tolerance_calculator/1d/water/"
mdl_path = "/users/ekb16170/tolerance_calculator/1d/water/model.mdl"
sh_path = "/users/ekb16170/tolerance_calculator/1d/water/main_script.sh"

for i in range(-12, 1, 1):
	tol_ls.append('1.e'+ str(i))

for tol in tol_ls:
	os.mkdir(os.path.join(root_dir, tol))

	target_mdl_path = root_dir + tol + "/model.mdl"
	target_sh_path = root_dir + tol + "/main_script.sh"

	shutil.copyfile(mdl_path, target_mdl_path)
	shutil.copyfile(sh_path, target_sh_path)

	with open(target_sh_path, 'r') as file:
		filedata = file.read()

	filedata = filedata.replace('FISH', tol)
	
	with open(target_sh_path, 'w') as file:
		file.write(filedata)

	bash_command = "bash main_script.sh"
	cwd = os.getcwd()
	os.chdir(str(tol))
	subprocess.run(['bash','main_script.sh'])
	os.chdir(cwd)
