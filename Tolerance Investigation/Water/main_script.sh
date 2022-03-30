#!/bin/csh -f



cat > model.inp <<EOF

&PARAMETERS

OUTLST='xugc', THEORY='DRISM', CLOSUR='KH',

!grid

NR=16384, DR=0.025, routup=384, toutup=0,

!MDIIS

NIS=20, DELVV=0.3, TOLVV=FISH,

!iter

KSAVE=-1, KSHOW=1, maxste=10000,

!ElStat

SMEAR=1, ADBCOR=0.5,

!bulk solvent properties

TEMPER=298, DIEps=78.497,

NSP=1

/

&SPECIES

DENSITY=55.5d0,

MODEL="model.mdl"

/

EOF



rism1d model > model.out || goto error

