import os
import pandas as pd
import numpy as np
from Bio.PDB import PDBParser
import subprocess
from pathlib import Path

# ------------- CONFIGURABLE PATHS -------------
pdb_dir = "path/to/your/pdb_directory"        # Directory containing PDB files
stride_executable = "path/to/stride_executable"  # Path to your STRIDE executable
output_csv = "structure_analysis_results.csv"    # Output CSV file
# ----------------------------------------------

# Initialize PDB parser (supresses warnings)
parser = PDBParser(QUIET=True)

def calculate_average_plddt(pdb_file):
    """
    Calculates the mean pLDDT of all atoms in a PDB file.
    pLDDT scores are assumed to be stored in the B-factor field.
    """
    try:
        structure = parser.get_structure("structure", pdb_file)
        # Collect all B-factors
        b_factors = [
            atom.bfactor
            for model in structure
            for chain in model
            for residue in chain
            for atom in residue
        ]
        
        if not b_factors:
            print(f"Warning: No B-factors found in {pdb_file}")
            return np.nan
        
        return np.mean(b_factors)
    except Exception as e:
        print(f"Error processing {pdb_file}: {str(e)}")
        return np.nan

def get_stride_secondary_structure_counts(pdb_file):
    """
    Runs STRIDE on a PDB file and returns a dictionary with counts
    of each secondary structure code. STRIDE typically uses:
      H: Alpha helix
      G: 3_10 helix
      I: Pi helix
      E: Extended strand
      B: Isolated beta-bridge
      T: Hydrogen-bonded turn
      C: Coil
      S: Bend (sometimes reported)
    """
    # Initialize all possible STRIDE codes to 0
    ss_codes = {"H": 0, "G": 0, "I": 0, "E": 0, "B": 0, "T": 0, "C": 0, "S": 0}
    
    try:
        # Run STRIDE and capture its output
        stride_output = subprocess.run(
            [stride_executable, pdb_file],
            capture_output=True,
            text=True,
            check=True
        )
        stride_data = stride_output.stdout
        
        # Each line describing a residue typically starts with 'ASG' in STRIDE output.
        # The one-letter secondary structure code is usually found at a specific column (around index 24).
        # You may need to adjust if your STRIDE version differs.
        for line in stride_data.splitlines():
            if line.startswith("ASG"):
                # Extract SS code (column 25 if counting from 1, or index 24 if from 0)
                ss_code = line[24]
                
                if ss_code in ss_codes:
                    ss_codes[ss_code] += 1
                    
        return ss_codes

    except subprocess.CalledProcessError as e:
        print(f"STRIDE error for {pdb_file}: {str(e)}")
        return {k: np.nan for k in ss_codes.keys()}
    except Exception as e:
        print(f"Error processing {pdb_file} with STRIDE: {str(e)}")
        return {k: np.nan for k in ss_codes.keys()}


def main():
    # Retrieve all PDB files from the specified directory
    pdb_files = list(Path(pdb_dir).glob("*.pdb"))
    total_files = len(pdb_files)
    print(f"Found {total_files} PDB files to process in '{pdb_dir}'")

    results = []
    processed_files = 0
    failed_files = 0

    # Process each PDB file
    for pdb_file in pdb_files:
        try:
            # Use the file stem (filename without extension) as protein ID
            protein_id = pdb_file.stem

            # Calculate average pLDDT
            plddt = calculate_average_plddt(pdb_file)

            # Get secondary structure counts from STRIDE
            ss_dict = get_stride_secondary_structure_counts(pdb_file)

            # Prepare result record
            record = {
                'protein_id': protein_id,
                'pLDDT': plddt
            }
            # Merge STRIDE codes into the record (e.g., 'H': #, 'G': #, etc.)
            record.update(ss_dict)

            results.append(record)
            processed_files += 1

            # Optional progress update
            if processed_files % 10 == 0:
                print(f"Processed {processed_files}/{total_files} files...")

        except Exception as e:
            print(f"Failed to process {pdb_file}: {str(e)}")
            failed_files += 1

    # Convert results to a DataFrame
    df = pd.DataFrame(results)

    # Print a brief summary
    print("\nProcessing Summary:")
    print(f"Total files processed successfully: {processed_files}")
    print(f"Failed files: {failed_files}")

    # Basic statistics on columns of interest
    print("\n--- pLDDT Stats ---")
    print(df['pLDDT'].describe())

    print("\n--- STRIDE Secondary Structure Counts (summary) ---")
    for ss_code in ["H", "G", "I", "E", "B", "T", "C", "S"]:
        if ss_code in df.columns:
            print(f"{ss_code} stats:")
            print(df[ss_code].describe())
            print()

    # Save results to CSV
    df.to_csv(output_csv, index=False)
    print(f"Results saved to: {output_csv}")


if __name__ == "__main__":
    main()

