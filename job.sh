#! /bin/bash
__conda_setup="$('/nfs/pic.es/user/m/mseglara/mambaforge/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
eval "$__conda_setup"
conda activate tilepy2
ID=$1
echo "Running job: ID=$ID"
python /data/cta/users-ifae/mseglara/science-data-challenge-gw/RunTiling.py $ID -c alpha  -i /data/cta/users-ifae/mseglara/cta-gwfollowup-simulations/v3_CTA_consortium/  -o /data/cta/users-ifae/mseglara/science-data-challenge-gw/output/  -params /data/cta/users-ifae/mseglara/science-data-challenge-gw/config/sdc.ini -ct sdc -t fixed 
echo "Job finished"