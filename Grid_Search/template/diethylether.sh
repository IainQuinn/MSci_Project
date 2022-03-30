#!/bin/csh -f

cat > diethylether.inp <<EOF
&PARAMETERS
THEORY='DRISM', CLOSURE='kh',        								!Theory
NR=16384, DR=0.025,                  								!Grid size and spacing
OUTLIST='uxgc', ROUT=384, KOUT=0,              			!Output
MDIIS_NVEC=20, MDIIS_DEL=0.1, TOLERANCE=1.e-12, MDIIS_RESTART=100,  !MDIIS
KSAVE=-1,                            								!Check pointing
PROGRESS=1,                         			 					!Output frequency
MAXSTEP=1000, EXTRA_PRECISION=1,                    				!Maximum iterations
SMEAR=1, ADBCOR=0.5,                 								!Electrostatics
TEMPERATURE=298.15, DIEPS=2, NSP=1 								!bulk solvent properties
/
        &SPECIES                               !solvent
        units='1/A^3',
        DENSITY=5.792885e-03,
        MODEL="edit.mdl"
/
EOF

rism1d diethylether > diethylether.out || goto error
