#!/bin/bash

# can be overruled on CLI with -J <NAME>
#SBATCH --job-name=devel

# Set the file to write the stdout and stderr to (if -e is not set; -o or --output).
#SBATCH --output=logs/%x-%j.log

# Set the number of cores (-n or --ntasks).
#SBATCH --ntasks=2

# Force allocation of the two cores on ONE node.
#SBATCH --nodes=1

# Set the memory per CPU. Units can be given in T|G|M|K.
#SBATCH --mem-per-cpu=500M

# Set the partition to be used (-p or --partition).
#SBATCH --partition=long

# Set the expected running time of your job (-t or --time).
# Formats are MM:SS, HH:MM:SS, Days-HH, Days-HH:MM, Days-HH:MM:SS
#SBATCH --time=20:00:00


export LOGDIR=logs/${SLURM_JOB_NAME}-${SLURM_JOB_ID}
export TMPDIR=/fast/users/${USER}/scratch/tmp;
mkdir -p $LOGDIR;

set -x;

unset DRMAA_LIBRARY_PATH
eval "$($(which conda) shell.bash hook)"  # ??
# somehow my environments are not set
# have to set it explicitly
conda activate WES-env;
echo $CONDA_PREFIX "activated";




# !!! leading white space is important
DRMAA=" -p medium -t 01:30 --mem-per-cpu=3000 --nodes=1 -n {threads}";
DRMAA="$DRMAA -o logs/%x-%j.log";
snakemake --unlock --rerun-incomplete;
snakemake --dag | dot -Tsvg > dax/dag.svg;
snakemake --use-conda --rerun-incomplete --drmaa "$DRMAA" -prk -j 500;
# -k ..keep going if job fails
# -p ..print out shell commands
