import glob
import os
import shutil 
import math

ROOT_DIR = '/users/ekb16170/gaussian/diethylether/dimer_C/'
OUTPUT_DIR = f'{ROOT_DIR}diethylether/diethylether/dimer_C/' 

with open(ROOT_DIR + "dimer_C.com", "r") as f:
	lines = f.read().splitlines()

new_lines = []
theta = float(90)

for line in lines:
	if "Fragment=2" in line:
		#line_start, zcoord = line.rsplit(" ", 1)
		line_start, x, y, z = line.split()		
		new_x = str(round(float(x) * math.cos(theta) - float(y) * math.sin(theta), 5))
		new_y = str(round(float(x) * math.sin(theta) +float(y) * math.cos(theta), 3))
		#new_z = str(round(float(z) + 5, 3))
		new_line = line_start + f" {new_x}"+ f" {new_y}"+ f" {z}"
		#new_line = line_start + f" {new_z}"

	else:
		new_line = line
	new_lines.append(new_line)

with open(ROOT_DIR + "dimer_C_new.com", "w+") as f:
	for line in new_lines:
		f.write(f"{line}\n")


