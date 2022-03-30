import glob
import os
import pathlib
import subprocess

ROOT_DIR = pathlib.Path.cwd()
# Put in your chosen directory
ROOT_DIR = pathlib.Path("/users/ekb16170/rism/diethylether_pdb")

os.chdir(ROOT_DIR)

for path in ROOT_DIR.glob("*.xyz"):
    with open(path, "r") as f:
        lines = f.readlines()
    an_to_ele = {
        1: "H",
        6: "C",
        7: "N",
        8: "O",
        9: "F",
        14: "Si",
        15: "P",
        16: "S",
        17: "Cl",
        35: "Br",
        53: "I",
    }
    # Run through each line and count 1 every time you see one starting with a space,
    # skipping blank line, i.e., counts only atoms
    n_atoms = sum(1 if line.startswith(" ") else 0 for line in lines)

    new_lines = []
    # Add number of atoms to 1st line with space between that and coordinates
    new_lines.append(str(n_atoms) + "\n")
    new_lines.append(lines[1])
    for i, line in enumerate(lines):
        if line.startswith(" "):
            # Slightly complicated one-liner that does:
            #   1. Grab the first 3 characters from the line
            #   2. Convert to an integer (this ignores spaces at the start)
            #   3. Look up in the dict `an_to_ele` for chemical symbol
            #   5. Left-justify toi ensure the symbol takes up 2 spaces (even if only 1 letter)
            #   6. Add the rest of the original line
            #   7. Appends to the list of lines to be written out
            new_lines.append(f"{an_to_ele[int(line[:3])].ljust(2)}" + line[3:])

    with open(path.stem + ".xyz", "w+") as f:
        for line in new_lines:
            f.write(line)

#subprocess.run(f'obabel *.xyz -opdb -m', shell=True)

