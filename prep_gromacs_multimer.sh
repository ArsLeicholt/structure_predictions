#!/bin/bash

#BATCH --nodes=1
#SBATCH --ntasks-per-node=36 
#SBATCH --mem=92G
#SBATCH --partition=partition_name
#SBATCH --time=04:00:00
#SBATCH --job-name=output
#SBATCH --output=output
#SBATCH --mail-type=ALL
#SBATCH --mail-user=youremail@domain.de

module --force purge

ml GCC/           #load your modules
ml CUDA/
ml OpenMPI/
ml GROMACS/

# Step 1: Convert PDB to GROMACS format, allowing for multiple chains
gmx pdb2gmx -f your_protein.pdb -o your_protein.gro -water spce -ignh -ff oplsaa -chainsep ter

gmx editconf -f your_protein.gro -o your_protein_box.gro -c -d 1.0 -bt cubic

gmx solvate -cp your_protein_box.gro -cs spc216.gro -o your_protein_solv.gro -p topol.top

gmx grompp -f ions.mdp -c your_protein_solv.gro -p topol.top -o your_protein_ions.tpr

echo "13" | gmx genion -s your_protein_ions.tpr -o your_protein_solv_ions.gro -p topol.top -pname NA -nname CL -neutral

gmx grompp -f minim.mdp -c your_protein_solv_ions.gro -p topol.top -o em.tpr
gmx mdrun -v -deffnm em

gmx grompp -f nvt.mdp -c em.gro -r em.gro -p topol.top -o nvt.tpr
gmx mdrun -v -deffnm nvt

gmx grompp -f npt.mdp -c nvt.gro -r nvt.gro -t nvt.cpt -p topol.top -o npt.tpr
gmx mdrun -v -deffnm npt

gmx grompp -f md.mdp -c npt.gro -t npt.cpt -p topol.top -o md_0_1.tpr

