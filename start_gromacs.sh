#!/bin/bash

#BATCH --nodes=1
#SBATCH --ntasks-per-node=36 
#SBATCH --mem=92G
#SBATCH --partition=partition_name
#SBATCH --time=168:00:00
#SBATCH --job-name=output
#SBATCH --output=output
#SBATCH --mail-type=ALL
#SBATCH --mail-user=youremail@domain.de

module --force purge

ml GCC/           #load your modules
ml CUDA/
ml OpenMPI/
ml GROMACS/

#export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so

export OMP_NUM_THREADS=1

# Then start gromacs like this:

srun --mpi=pmix_v3 -N 1 -n 36 gmx_mpi mdrun -v -deffnm md_0_1

