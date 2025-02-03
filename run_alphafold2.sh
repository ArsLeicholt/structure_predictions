#!/bin/bash

#SBATCH --nodes=1                      # Request 1 compute node
#SBATCH --ntasks=16                    # Use 16 tasks (often 1 CPU core per task)
#SBATCH --cpus-per-task=1             # 1 CPU core per task
#SBATCH --mem=16G                      # Request 16 GB of memory
#SBATCH --partition=gpu                # Specify GPU partition
#SBATCH --gres=gpu:1                   # Request 1 GPU
#SBATCH --time=168:00:00               # Job time limit (168 hours)
#SBATCH --job-name=alphafold_run       # Descriptive job name
#SBATCH --mail-type=ALL                # Email on job begin, end, fail, etc.
#SBATCH --mail-user=your_email@domain  # Email address for notifications
#SBATCH --array=1-2000%2               # Array: indices 1 to 2000, max 2 at once, can differ

module --force purge                   # Unload all current modules
module load GCC/11.3.0                 # Load compiler/toolchain
module load OpenMPI/4.1.4              # Load MPI for parallel tasks
module load AlphaFold/2.3.1-CUDA-11.7.0 # Load AlphaFold module
export ALPHAFOLD_DATA_DIR=/path/to/alphafold/data # Set AlphaFold data path

cd /scratch/tmp/username/alphafold_runs # Change to working directory

alphafold \
  --fasta_paths=/scratch/tmp/username/alphafold_runs/fasta/seq_${SLURM_ARRAY_TASK_ID}.fa \  # Input FASTA
  --model_preset=monomer               # Use monomer model or multimer
  --output_dir=/scratch/tmp/username/alphafold_runs/results/${SLURM_ARRAY_TASK_ID}  # Output folder
  --max_template_date=2022-12-19       # Template cutoff date
  --db_preset=reduced_dbs              # Use reduced DBs for faster runs
  --data_dir=$ALPHAFOLD_DATA_DIR       # Point to database directory

wait                                   # Ensure all processes finish

