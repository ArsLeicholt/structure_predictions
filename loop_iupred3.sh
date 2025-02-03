#!/bin/bash

# Directory containing FASTA files
INPUT_DIR="/your/input/directory"  # Change this to your actual directory path
OUTPUT_DIR="iupred_results"
IUPRED_SCRIPT="iupred3.py"
IUPRED_TYPE="short"  # Change to "short" or "global" if needed
SMOOTHING="medium"  # Default smoothing

mkdir -p "$OUTPUT_DIR"

for fasta_file in "$INPUT_DIR"/*.fasta "$INPUT_DIR"/*.fa; do
    base_name=$(basename "$fasta_file" .fasta)
    base_name=$(basename "$base_name" .fa)
    output_csv="$OUTPUT_DIR/${base_name}.csv"

    # Get sequence length using awk
    seq_length=$(awk '/^>/ {next} {print length($0)}' "$fasta_file" | head -n 1)

    # Disable smoothing if sequence length < 19
    if [[ $seq_length -lt 19 ]]; then
        python3 "$IUPRED_SCRIPT" "$fasta_file" "$IUPRED_TYPE" -s "no" > "$output_csv"
    else
        python3 "$IUPRED_SCRIPT" "$fasta_file" "$IUPRED_TYPE" -s "$SMOOTHING" > "$output_csv"
    fi

    echo "Processed: $fasta_file -> $output_csv (Length: $seq_length)"
done

echo "All FASTA files processed. Results saved in $OUTPUT_DIR."

