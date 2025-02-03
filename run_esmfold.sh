#!/bin/bash

#SBATCH --job-name=esmfold_job       # Name of your job
#SBATCH --output=esmfold_%j.out      # Standard output (job ID in filename)
#SBATCH --error=esmfold_%j.err       # Standard error (job ID in filename)
#SBATCH --time=12:00:00              # Wall-clock time limit (HH:MM:SS)
#SBATCH --partition=gpu              # Partition/queue with GPUs
#SBATCH --gres=gpu:1                 # Number of GPUs (1 GPU)
#SBATCH --cpus-per-task=4            # Number of CPU cores per task
#SBATCH --mem=16G                    # Total memory
#SBATCH --mail-type=ALL              # Get emails on start/end/fail
#SBATCH --mail-user=your_email@domain.com


module load CUDA/11.7.0              # Load CUDA module (adjust version as needed)
module load Singularity              # Load Singularity for containerized execution

# Run ESMfold within a Singularity container
# --nv passes NVIDIA libraries for GPU usage
# --bind mounts host directories inside the container if needed (adjust paths accordingly)
singularity exec --nv \
    /path/to/esmfold_container.sif \
    python /app/esm/esmfold_inference.py \
        --fasta /path/to/input_sequences.fasta \
        --output /path/to/output_directory \
        --max-tokens-per-batch 1024 \
        --chunk-size 256

# Explanation of common flags:
# --fasta: Path to one or more protein sequences in FASTA format.
# --output: Where to store prediction outputs (PDB files, logs, etc.).
# --max-tokens-per-batch & --chunk-size: Control how batches are split for memory management.

wait  # Ensures all processes complete before the script ends

