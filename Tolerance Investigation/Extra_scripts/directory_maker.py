import os
import shutil
import subprocess

tol_ls = []
root_dir = "/users/ekb16170/tolerance_calculator/3d/diethylether/"
prmtop_path = "/users/ekb16170/tolerance_calculator/3d/diethylether/0008noc.prmtop"
pdb_path = "/users/ekb16170/tolerance_calculator/3d/diethylether/0008noc.pdb"

for i in range(-12, 1, 1):
	tol_ls.append('1.e'+ str(i))

for tol in tol_ls:
	os.mkdir(os.path.join(root_dir, tol))

	target_prmtop_path = root_dir + tol + "/0008noc.prmtop"
	target_pdb_path = root_dir + tol + "/0008noc.pdb"

	shutil.copyfile(prmtop_path, target_prmtop_path)
	shutil.copyfile(pdb_path, target_pdb_path)
