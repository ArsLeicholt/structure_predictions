#!/usr/bin/env python3
"""
Convert FASTA files to AlphaFold3 JSON input format.
Handles both single and multi-sequence FASTA files with two modes:
- Complex mode: All sequences in one JSON (predicts as multi-chain complex)
- Individual mode: One JSON per sequence (separate predictions)
"""

import json
import os
import argparse
import re
from pathlib import Path


def parse_fasta(fasta_file):
    """Parse FASTA file and return list of (header, sequence) tuples."""
    sequences = []
    current_header = None
    current_sequence = []
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_header is not None:
                    sequences.append((current_header, ''.join(current_sequence)))
                current_header = line[1:]  # Remove '>'
                current_sequence = []
            elif line:
                current_sequence.append(line)
    
    # Add the last sequence
    if current_header is not None:
        sequences.append((current_header, ''.join(current_sequence)))
    
    return sequences


def clean_sequence(sequence):
    """Remove any non-amino acid characters from sequence."""
    # Keep only standard amino acid letters
    return re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', sequence.upper())


def generate_chain_ids(num_sequences):
    """Generate chain IDs for sequences (A, B, C, ..., Z, AA, AB, ...)."""
    chain_ids = []
    for i in range(num_sequences):
        if i < 26:
            chain_ids.append(chr(ord('A') + i))
        else:
            # For more than 26 sequences, use AA, AB, AC, etc.
            first = chr(ord('A') + (i // 26) - 1)
            second = chr(ord('A') + (i % 26))
            chain_ids.append(first + second)
    return chain_ids


def create_alphafold3_json(sequences, job_name, model_seeds=None):
    """Create AlphaFold3 JSON input from parsed sequences."""
    if model_seeds is None:
        model_seeds = [1]
    
    # Generate chain IDs
    chain_ids = generate_chain_ids(len(sequences))
    
    # Create the JSON structure
    af3_json = {
        "name": job_name,
        "sequences": [],
        "modelSeeds": model_seeds,
        "dialect": "alphafold3",
        "version": 1
    }
    
    # Handle single sequence case
    if len(sequences) == 1:
        _, sequence = sequences[0]
        cleaned_seq = clean_sequence(sequence)
        af3_json["sequences"].append({
            "protein": {
                "id": [chain_ids[0]],
                "sequence": cleaned_seq
            }
        })
    else:
        # Handle multiple sequences (complex)
        for i, (header, sequence) in enumerate(sequences):
            cleaned_seq = clean_sequence(sequence)
            af3_json["sequences"].append({
                "protein": {
                    "id": [chain_ids[i]],
                    "sequence": cleaned_seq
                }
            })
    
    return af3_json


def process_fasta_file(fasta_file, output_dir, model_seeds=None, split_sequences=False):
    """Process a single FASTA file and create corresponding JSON(s)."""
    fasta_path = Path(fasta_file)
    base_job_name = fasta_path.stem  # Filename without extension
    
    # Parse sequences
    sequences = parse_fasta(fasta_file)
    
    if not sequences:
        print(f"Warning: No sequences found in {fasta_file}")
        return []
    
    output_files = []
    
    if split_sequences:
        # Create one JSON file per sequence
        for i, (header, sequence) in enumerate(sequences):
            # Clean up header for filename (remove problematic characters)
            clean_header = re.sub(r'[^\w\-_.]', '_', header)
            if len(clean_header) > 50:  # Truncate very long headers
                clean_header = clean_header[:50]
            
            job_name = f"{base_job_name}_{i+1:03d}_{clean_header}"
            
            # Create JSON for single sequence
            af3_json = create_alphafold3_json([(header, sequence)], job_name, model_seeds)
            
            # Write JSON file
            output_file = Path(output_dir) / f"{job_name}.json"
            with open(output_file, 'w') as f:
                json.dump(af3_json, f, indent=2)
            
            print(f"Created: {output_file}")
            print(f"  - Job name: {job_name}")
            print(f"  - Header: {header}")
            print(f"  - Sequence length: {len(clean_sequence(sequence))}")
            
            output_files.append(output_file)
    
    else:
        # Create single JSON file with all sequences (original behavior)
        af3_json = create_alphafold3_json(sequences, base_job_name, model_seeds)
        
        # Write JSON file
        output_file = Path(output_dir) / f"{base_job_name}.json"
        with open(output_file, 'w') as f:
            json.dump(af3_json, f, indent=2)
        
        print(f"Created: {output_file}")
        print(f"  - Job name: {base_job_name}")
        print(f"  - Sequences: {len(sequences)}")
        print(f"  - Chain IDs: {[seq['protein']['id'][0] for seq in af3_json['sequences']]}")
        
        output_files.append(output_file)
    
    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Convert FASTA files to AlphaFold3 JSON input format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single FASTA file (all sequences as complex)
  python fasta_to_json.py input.fasta -o output_dir/
  
  # Split multi-sequence FASTA into individual predictions
  python fasta_to_json.py input.fasta -o output_dir/ --split
  
  # Process all FASTA files in directory with splitting
  python fasta_to_json.py fasta_dir/ -o output_dir/ --split
  
  # Process with custom model seeds
  python fasta_to_json.py input.fasta -o output_dir/ --model-seeds 1 2 3 --split
        """
    )
    
    parser.add_argument("input", 
                       help="Input FASTA file or directory containing FASTA files")
    parser.add_argument("-o", "--output", required=True,
                       help="Output directory for JSON files")
    parser.add_argument("--model-seeds", nargs="+", type=int, default=[1],
                       help="Model seeds for AlphaFold3 (default: [1])")
    parser.add_argument("--extensions", nargs="+", 
                       default=[".fasta", ".fas", ".fa", ".faa"],
                       help="FASTA file extensions to process (default: .fasta .fas .fa .faa)")
    parser.add_argument("--split", action="store_true",
                       help="Split multi-sequence FASTA files into individual JSON files (one per sequence)")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input_path = Path(args.input)
    processed_files = []
    
    if input_path.is_file():
        # Process single file
        if input_path.suffix.lower() in [ext.lower() for ext in args.extensions]:
            results = process_fasta_file(input_path, output_dir, args.model_seeds, args.split)
            processed_files.extend(results)
        else:
            print(f"Warning: {input_path} does not have a recognized FASTA extension")
    
    elif input_path.is_dir():
        # Process all FASTA files in directory
        for ext in args.extensions:
            pattern = f"*{ext}"
            fasta_files = list(input_path.glob(pattern))
            fasta_files.extend(input_path.glob(pattern.upper()))
            
            for fasta_file in fasta_files:
                results = process_fasta_file(fasta_file, output_dir, args.model_seeds, args.split)
                processed_files.extend(results)
    
    else:
        print(f"Error: {input_path} is neither a file nor a directory")
        return 1
    
    # Summary
    print(f"\nProcessing complete!")
    print(f"Created {len(processed_files)} JSON files in {output_dir}")
    
    # Create total_jobs.txt file for the SLURM script
    total_jobs_file = output_dir / "../total_jobs.txt"
    with open(total_jobs_file, 'w') as f:
        f.write(str(len(processed_files)))
    print(f"Created {total_jobs_file} with total job count: {len(processed_files)}")
    
    return 0


if __name__ == "__main__":
    exit(main())
