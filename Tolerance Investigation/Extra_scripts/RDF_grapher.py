import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os 
import shutil

def clean_txt(file_path):
    with open(file_path, "r+") as f:
        lines = f.readlines()
        del lines[0:3]
        f.seek(0)
        f.truncate()
        f.writelines(lines)
        
root_dir = "/users/ekb16170/tolerance_calculator/1d/diethylether/"

#------------------------------------------------------------------------------------------------------

for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        file_path = os.path.join(directory, file)
        new_file_path = os.path.join(directory, "model.txt")
        
        if file.endswith(".gvv"):
            shutil.copyfile(file_path, new_file_path)
            clean_txt(new_file_path)
            df = pd.read_fwf(new_file_path)
            del df[df.columns[0]]
            df.to_csv(os.path.join(directory, (os.path.basename(directory) + '(GVV).csv')))

        if file.endswith(".cvv"):
            shutil.copyfile(file_path, new_file_path)
            clean_txt(new_file_path)
            df = pd.read_fwf(new_file_path)
            del df[df.columns[0]]
            df.to_csv(os.path.join(directory, (os.path.basename(directory) + '(CVV).csv')))
        
        if file.endswith(".uvv"):
            shutil.copyfile(file_path, new_file_path)
            clean_txt(new_file_path)
            df = pd.read_fwf(new_file_path)
            del df[df.columns[0]]
            df.to_csv(os.path.join(directory, (os.path.basename(directory) + '(UVV).csv')))
            
#------------------------------------------------------------------------------------------------------            

plt.clf()
plt.figure(dpi=400)


for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(GVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["OS:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("OS:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("G(r)")
            plt.savefig(os.path.join(root_dir, 'OS:OS_GVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(CVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["OS:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("OS:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("C(r)")
            plt.savefig(os.path.join(root_dir, 'OS:OS_CVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(UVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            #df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["OS:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("OS:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("Energy(kt)")
            plt.savefig(os.path.join(root_dir, 'OS:OS_UVV.png'))
plt.clf()
#--------------------------------------------------------------------------------------
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(GVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("G(r)")
            plt.savefig(os.path.join(root_dir, 'CH2:OS_GVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(CVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("C(r)")
            plt.savefig(os.path.join(root_dir, 'CH2:OS_CVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(UVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            #df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:OS"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:OS")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("Energy(kt)")
            plt.savefig(os.path.join(root_dir, 'CH2:OS_UVV.png'))
plt.clf()

#--------------------------------------------------------------------------------------

for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(GVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:CH2"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:CH2")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("G(r)")
            plt.savefig(os.path.join(root_dir, 'CH2:CH2_GVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(CVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:CH2"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:CH2")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("C(r)")
            plt.savefig(os.path.join(root_dir, 'CH2:CH2_CVV.png'))
plt.clf()
            
for directory, subdirectories, files in os.walk(root_dir):
    for file in files:
        
        if '(UVV)' in file:
            file_path = os.path.join(directory, file)
            df = pd.read_csv(file_path)
            #df = df.loc[df["SEPARATION"] <10]
            plt.plot(df["SEPARATION"], df["CH2:CH2"], label=file[:-9])
            plt.legend(loc='center right')
            plt.title("CH2:CH2")
            plt.xlabel("Distance (Angstroms)")
            plt.ylabel("Energy(kt)")
            plt.savefig(os.path.join(root_dir, 'CH2:CH2_UVV.png'))
plt.clf()
