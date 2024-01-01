#!/bin/bash
#
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH -t 0-05:30 # Runtime in D-HH:MM

#SBATCH --cpus-per-task=1 # Request that ncpus be allocated per process.
#SBATCH --mem=50g # Memory pool for all cores (see also --mem-per-cpu)

# Change to the directory that the script was launched from. This is the default for SLURM.

module load python/3.7.0

thread_idx=20

this_period="overnight"

log_name="/ihome/kpelechrinis/xil178/simulation_chicago"
log_name+="_${this_period}_${thread_idx}.txt"

# Run the job
python simulation_chicago_period_b_nb.py\
    --thread $thread_idx\
    --start_B B\
    --end_B B\
    --period $this_period\
    &> $log_name

