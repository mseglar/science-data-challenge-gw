batch_count = 5  # adjust to your splits

for i in range(batch_count):
    with open(f"job_batch_{i}.sub", "w") as f:
        f.write(
            f"""
executable = /data/cta/users-ifae/mseglara/science-data-challenge-gw/job.sh

arguments = $(ID) 
output = /data/cta/scratch/mseglara/sdc/log/out/condor_$(ID).txt
error  = /data/cta/scratch/mseglara/sdc/log/error/condor_$(ID).txt
log    =  /data/cta/scratch/mseglara/sdc/log/log/condor_$(ID).txt

request_memory = 16384
request_cpus = 2
+experiment = "cta"

queue ID from /data/cta/users-ifae/mseglara/science-data-challenge-gw/params_batch_{i}.txt

"""
        )
