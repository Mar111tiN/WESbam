#!/bin/bash

# can be overruled on CLI with -J <NAME>
#SBATCH --job-name=WESbam
#SBATCH --output=slogs/%x-%j.log
#SBATCH --ntasks=2
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=500M
#SBATCH --partition=long
#SBATCH --time=20:00:00

export LOGDIR=${HOME}/scratch/slogs/${SLURM_JOB_NAME}-${SLURM_JOB_ID}
export TMPDIR=/fast/users/${USER}/scratch/tmp;
mkdir -p $LOGDIR;

set -x;

# make conda available
eval "$($(which conda) shell.bash hook)"
# activate snakemake env
conda activate snake-env;
echo $CONDA_PREFIX "activated";

SLURM_CLUSTER="sbatch -p {cluster.partition} -t {cluster.t} --mem-per-cpu={cluster.memory} -J {cluster.name} --nodes={cluster.nodes} -n {cluster.threads}";
SLURM_CLUSTER="$SLURM_CLUSTER -o ${LOGDIR}/{rule}-%j.log";
snakemake --unlock;
snakemake --dag | awk '$0 ~ "digraph" {p=1} p'| dot -Tsvg > dax/dag.svg;
snakemake --use-conda \
--rerun-incomplete \
--cluster-config configs/cluster/cluster_slurm.json \
--cluster "$SLURM_CLUSTER" \
-prkj 1000;
