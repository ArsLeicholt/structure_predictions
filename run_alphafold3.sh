#!/bin/bash

#SBATCH --nodes=1                      # Request 1 compute node
#SBATCH --ntasks=16                    # Use 16 tasks (often 1 CPU core per task)
#SBATCH --cpus-per-task=1             # 1 CPU core per task
#SBATCH --mem=16G                      # Request 60 GB of memory
#SBATCH --partition=gpu                # Specify GPU partition
#SBATCH --gres=gpu:1                   # Request 1 GPU
#SBATCH --time=168:00:00               # Job time limit (168 hours)
#SBATCH --job-name=alphafold_run       # Descriptive job name
#SBATCH --mail-type=ALL                # Email on job begin, end, fail, etc.
#SBATCH --mail-user=your_email@domain  # Email address for notifications

module --force purge                   
module load AlphaFold                # Load AlphaFold module (adapt as needed)
singularity exec \			# singularity execution (might also be apptainer)
    --nv                                            # Enable NVIDIA GPU support
    --bind $HOME/:/root/af_input \                  # Bind local HOME to container's /root/af_input
    --bind $HOME/:/root/af_output \                 # Bind local HOME to container's /root/af_output
    --bind /software/sit/images/alphafold/3.0.0/models/:/root/models \ # Bind model directory
    --bind /db/alphafold3/202412/:/root/public_databases \# Bind AlphaFold databases
    /software/sit/images/alphafold/3.0.0/alphafold-3.0.0.sif \# Path to the Singularity image
    python $HOME//alphafold3/run_alphafold.py \              # Python script entry point
    --json_path=input.json \                  # JSON input specifying sequences and settings
    --output_dir=./output/ \                                # Output results directory
    --run_data_pipeline=False \                       # Whether to run or skip data pipeline
    --model_dir=/root/models                         # Location of AlphaFold model parameters

