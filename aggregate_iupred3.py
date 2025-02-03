import os
import pandas as pd
import argparse

def process_iupred_csv(csv_file):
    """
    Reads an IUPred3 CSV file and calculates median disorder and fraction of disorder-promoting residues.
    """
    try:
        # Load CSV, assuming it has headers: POS, RES, IUPRED2
        df = pd.read_csv(csv_file, sep="\t", comment="#", header=None, names=["position", "residue", "disorder_score"])

        # Compute statistics
        median_disorder = df["disorder_score"].median()
        fraction_disordered = (df["disorder_score"] >= 0.5).mean()

        return median_disorder, fraction_disordered
    except Exception as e:
        print(f"Error processing {csv_file}: {e}")
        return None, None


def aggregate_results(input_dir, output_file):
    """
    Processes all CSV files in input_dir and saves results to output_file.
    """
    results = []

    for csv_file in os.listdir(input_dir):
        if csv_file.endswith(".csv"):
            file_path = os.path.join(input_dir, csv_file)
            filename_without_extension = os.path.splitext(csv_file)[0]

            median_disorder, fraction_disordered = process_iupred_csv(file_path)
            if median_disorder is not None:
                results.append([filename_without_extension, median_disorder, fraction_disordered])

    # Save to CSV
    df_results = pd.DataFrame(results, columns=["filename", "median_disorder", "fraction_disordered"])
    df_results.to_csv(output_file, index=False)

    print(f"Summary saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate IUPred3 disorder results.")
    parser.add_argument("input_dir", help="Directory containing IUPred3 CSV files")
    parser.add_argument("output_file", help="Path to output CSV file")

    args = parser.parse_args()
    aggregate_results(args.input_dir, args.output_file)

