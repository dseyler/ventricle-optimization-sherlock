#!/usr/bin/env python3
"""
CSV Processing Script

This script processes the ventricle_analysis_results.csv file to remove lines where
the volume exceeds 2x the initial volume for each case_name.

Usage:
    python3 csv_processing.py [input_csv] [output_csv]
    
If no arguments are provided, it will process ventricle_analysis_results.csv 
and create ventricle_analysis_results_filtered.csv
"""

import pandas as pd
import sys
import os
import argparse


def process_csv(input_file, output_file=None):
    """
    Process CSV file to remove lines where volume > 2x initial volume for each case.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file (optional)
    """
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False
    
    print(f"Reading CSV file: {input_file}")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df)} rows from CSV file")
        
        # Check required columns
        required_columns = ['case_name', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Error: Missing required columns: {missing_columns}")
            return False
        
        # Calculate initial volume for each case (assuming time_step=0 or earliest time)
        print("Calculating initial volumes for each case...")
        
        # Group by case_name and find the initial volume (minimum time step)
        initial_volumes = {}
        filtered_data = []
        
        for case_name in df['case_name'].unique():
            case_data = df[df['case_name'] == case_name].copy()
            
            # Sort by time_step to ensure we get the initial volume
            case_data = case_data.sort_values('time_step')
            
            # Get initial volume (first row after sorting)
            initial_volume = case_data['volume'].iloc[0]
            initial_volumes[case_name] = initial_volume
            
            print(f"  {case_name}: initial volume = {initial_volume:.2f}")
            
            # Filter data where volume <= 2 * initial_volume
            volume_threshold = 2 * initial_volume
            filtered_case_data = case_data[case_data['volume'] <= volume_threshold]
            
            removed_rows = len(case_data) - len(filtered_case_data)
            if removed_rows > 0:
                print(f"  {case_name}: removed {removed_rows} rows where volume > {volume_threshold:.2f}")
            
            filtered_data.append(filtered_case_data)
        
        # Combine all filtered data
        if filtered_data:
            filtered_df = pd.concat(filtered_data, ignore_index=True)
        else:
            filtered_df = pd.DataFrame()
        
        # Sort by case_name and time_step
        filtered_df = filtered_df.sort_values(['case_name', 'time_step']).reset_index(drop=True)
        
        # Summary statistics
        original_rows = len(df)
        filtered_rows = len(filtered_df)
        removed_rows = original_rows - filtered_rows
        
        print(f"\nProcessing Summary:")
        print(f"  Original rows: {original_rows}")
        print(f"  Filtered rows: {filtered_rows}")
        print(f"  Removed rows: {removed_rows}")
        print(f"  Percentage removed: {(removed_rows/original_rows)*100:.1f}%")
        
        # Save filtered data
        if output_file is None:
            # Create output filename based on input filename
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_filtered.csv"
        
        print(f"\nSaving filtered data to: {output_file}")
        filtered_df.to_csv(output_file, index=False)
        
        print("Processing completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to handle command line arguments and run processing."""
    
    parser = argparse.ArgumentParser(
        description="Filter CSV file to remove rows where volume > 2x initial volume for each case",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 csv_processing.py
    python3 csv_processing.py ventricle_analysis_results.csv
    python3 csv_processing.py input.csv output_filtered.csv
        """
    )
    
    parser.add_argument(
        'input_file', 
        nargs='?', 
        default='ventricle_analysis_results.csv',
        help='Input CSV file (default: ventricle_analysis_results.csv)'
    )
    
    parser.add_argument(
        'output_file', 
        nargs='?', 
        default=None,
        help='Output CSV file (default: input_file_filtered.csv)'
    )
    
    args = parser.parse_args()
    
    # Run the processing
    success = process_csv(args.input_file, args.output_file)
    
    if success:
        print("\nScript completed successfully!")
        sys.exit(0)
    else:
        print("\nScript failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
