import os
import shutil
import glob
import subprocess
import time
import pandas as pd
import re

root_dir = "/users/ekb16170/tolerance_calculator/3d/diethylether/"

dic = {}

for directory, subdirectories, files in os.walk(root_dir):
	for file in files:

		if file.endswith(".log"):
			print(directory + "/" + file)

			with open(directory + "/" + file) as f:

				for i, line in enumerate(f):
					if i == 68:
						e1 = float(line[42:59])
					if i == 69:
						e2 = float(line[42:59])
					if i == 70:
						e3 = float(line[42:59])
				#print(e1, e2, e3)
				dic[re.findall("\d+", directory[-5:])[0]]= [e1, e2, e3]

df = pd.DataFrame.from_dict(dic)
df.insert(0, "energy", ['excessChemicalPotentialGF', 'excessChemicalPotentialPCPLUS', 'solventPotentialEnergy'], True)
df.to_csv(root_dir + 'df.csv')

