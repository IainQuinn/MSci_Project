#!/bin/csh -f

cat > model.inp <<EOF

&PARAMETERS
THEORY='DRISM', CLOSURE='kh',        								!Theory
NR=16384, DR=0.025,                  								!Grid size and spacing
OUTLIST='xugc', ROUT=384, KOUT=0,       								!Output
MDIIS_NVEC=20, MDIIS_DEL=0.1, TOLERANCE=FISH, MDIIS_RESTART=100,    !MDIIS
KSAVE=-1,                            								!Check pointing
PROGRESS=1,                         			 					!Output frequency
MAXSTEP=1000, EXTRA_PRECISION=1,                    				!Maximum iterations
SMEAR=1, ADBCOR=0.5,                 								!Electrostatics
TEMPERATURE=298.15, DIEPS=4.33, NSP=1 								!bulk solvent properties
/
        &SPECIES                               !solvent
        units='1/A^3',
        DENSITY=5.792885e-03,
        MODEL="model.mdl"
/

EOF

rism1d model > model.out || goto error



