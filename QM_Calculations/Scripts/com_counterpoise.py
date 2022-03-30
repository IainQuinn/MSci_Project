import glob
import os
import shutil

ROOT_DIR = '/users/ekb16170/gaussian/'
OUTPUT_DIR = f'{ROOT_DIR}diethylether/dimer_C/'

os.chdir(OUTPUT_DIR)

n_files = 100
start_file = "dimer_C.com"


for n in range(1, n_files + 1):
    if n == 1:
        infile = start_file
        outfile = start_file.replace(".com", f"_{n}.com")
    else:
        infile = start_file.replace(".com", f"_{n - 1}.com")
        outfile = start_file.replace(".com", f"_{n}.com")

    with open(infile, "r") as f:
        lines = f.read().splitlines()

    new_lines = []
    for line in lines:
        if "Fragment=2" in line:
#            line_start, zcoord = line.rsplit(" ", 1)
            line_start, x, y, z = line.split()		
            #new_x = str(round(float(x) + 0.1, 5))
            #new_y = str(round(float(y) + 0.1, 5))
            new_z = str(round(float(z) + 0.1, 5))
            new_line = line_start + f" {x}"+ f" {y}"+ f" {new_z}"
#            new_line = line_start + f" {new_z}"

        else:
            new_line = line
        new_lines.append(new_line)

    with open(outfile, "w+") as f:
        for line in new_lines:
            f.write(f"{line}\n")



