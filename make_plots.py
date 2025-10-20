#!/usr/bin/env python3
"""
Plotting Script for Ventricle Analysis Results

This script loads the ventricle_analysis_results.csv file and creates various plots:
1. Individual plots for each case showing volume vs strain/twist
2. Comparison plots for different cases
3. Helix angle comparison plots

Usage:
    python3 make_plots.py [csv_file]
    
If no csv_file is provided, it will use ventricle_analysis_results.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import argparse
from pathlib import Path


def create_plots_directory():
    """Create the plots directory if it doesn't exist."""
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)
    return plots_dir


def plot_individual_case(df, case_name, plots_dir):
    """
    Create individual plot for a case showing volume vs strain/twist.
    
    Args:
        df: DataFrame with the data
        case_name: Name of the case to plot
        plots_dir: Directory to save plots
    """
    
    case_data = df[df['case_name'] == case_name].copy()
    
    if case_data.empty:
        print(f"Warning: No data found for case {case_name}")
        return
    
    # Sort by volume
    case_data = case_data.sort_values('volume')
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle(f'Case: {case_name}', fontsize=16, fontweight='bold')
    
    # Plot circumferential strain
    ax1.plot(case_data['volume'], case_data['circumferential_strain'], 'b-', linewidth=2)
    ax1.set_ylabel('Circumferential Strain', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.set_title('Circumferential Strain vs Volume', fontsize=14)
    
    # Plot longitudinal strain
    ax2.plot(case_data['volume'], case_data['longitudinal_strain'], 'r-', linewidth=2)
    ax2.set_ylabel('Longitudinal Strain', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Longitudinal Strain vs Volume', fontsize=14)
    
    # Plot twist angle
    ax3.plot(case_data['volume'], case_data['twist_angle'], 'g-', linewidth=2)
    ax3.set_xlabel('Volume', fontsize=12)
    ax3.set_ylabel('Twist Angle', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.set_title('Twist Angle vs Volume', fontsize=14)
    
    plt.tight_layout()
    
    # Save plot
    output_file = plots_dir / f"{case_name}_individual.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved individual plot for {case_name}: {output_file}")


def plot_case_comparison(df, case_names, title, filename, plots_dir):
    """
    Create comparison plot for multiple cases.
    
    Args:
        df: DataFrame with the data
        case_names: List of case names to compare
        title: Plot title
        filename: Output filename
        plots_dir: Directory to save plots
    """
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
    
    for i, case_name in enumerate(case_names):
        case_data = df[df['case_name'] == case_name].copy()
        
        if case_data.empty:
            print(f"Warning: No data found for case {case_name}")
            continue
        
        # Sort by volume
        case_data = case_data.sort_values('volume')
        color = colors[i % len(colors)]
        
        # Plot circumferential strain
        ax1.plot(case_data['volume'], case_data['circumferential_strain'], 
                color=color, linewidth=2, label=case_name)
        
        # Plot longitudinal strain
        ax2.plot(case_data['volume'], case_data['longitudinal_strain'], 
                color=color, linewidth=2, label=case_name)
        
        # Plot twist angle
        ax3.plot(case_data['volume'], case_data['twist_angle'], 
                color=color, linewidth=2, label=case_name)
    
    # Set labels and formatting
    ax1.set_ylabel('Circumferential Strain', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_title('Circumferential Strain vs Volume', fontsize=14)
    
    ax2.set_ylabel('Longitudinal Strain', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_title('Longitudinal Strain vs Volume', fontsize=14)
    
    ax3.set_xlabel('Volume', fontsize=12)
    ax3.set_ylabel('Twist Angle', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    ax3.set_title('Twist Angle vs Volume', fontsize=14)
    
    plt.tight_layout()
    
    # Save plot
    output_file = plots_dir / filename
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved comparison plot: {output_file}")


def plot_helix_angle_comparison(df, helix_angles, circ_type, plots_dir):
    """
    Create helix angle comparison plot.
    
    Args:
        df: DataFrame with the data
        helix_angles: List of helix angles to compare
        circ_type: '0circ' or '2circ'
        plots_dir: Directory to save plots
    """
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    fig.suptitle(f'Helix Angle Comparison - {circ_type}', fontsize=16, fontweight='bold')
    
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, helix_angle in enumerate(helix_angles):
        case_name = f"8_{helix_angle}_{circ_type}"
        case_data = df[df['case_name'] == case_name].copy()
        
        if case_data.empty:
            print(f"Warning: No data found for case {case_name}")
            continue
        
        # Sort by volume
        case_data = case_data.sort_values('volume')
        color = colors[i % len(colors)]
        
        # Plot circumferential strain
        ax1.plot(case_data['volume'], case_data['circumferential_strain'], 
                color=color, linewidth=2, label=f'{helix_angle}°')
        
        # Plot longitudinal strain
        ax2.plot(case_data['volume'], case_data['longitudinal_strain'], 
                color=color, linewidth=2, label=f'{helix_angle}°')
        
        # Plot twist angle
        ax3.plot(case_data['volume'], case_data['twist_angle'], 
                color=color, linewidth=2, label=f'{helix_angle}°')
    
    # Set labels and formatting
    ax1.set_ylabel('Circumferential Strain', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(title='Helix Angle', fontsize=10)
    ax1.set_title('Circumferential Strain vs Volume', fontsize=14)
    
    ax2.set_ylabel('Longitudinal Strain', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(title='Helix Angle', fontsize=10)
    ax2.set_title('Longitudinal Strain vs Volume', fontsize=14)
    
    ax3.set_xlabel('Volume', fontsize=12)
    ax3.set_ylabel('Twist Angle', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(title='Helix Angle', fontsize=10)
    ax3.set_title('Twist Angle vs Volume', fontsize=14)
    
    plt.tight_layout()
    
    # Save plot
    output_file = plots_dir / f"helix_angle_comparison_{circ_type}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved helix angle comparison plot: {output_file}")


def plot_material_comparison(df, plots_dir):
    """
    Create material comparison plot for 8_30_0circ cases with different materials.
    
    Args:
        df: DataFrame with the data
        plots_dir: Directory to save plots
    """
    
    # Define material cases and their labels
    material_cases = [
        ('8_30_0circ', 'Smooth-Sil 960'),
        ('8_30_0circ_DS10', 'Dragonskin 10'),
        ('8_30_0circ_DS30', 'Dragonskin 30')
    ]
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    fig.suptitle('Material Comparison: 8_30_0circ Geometry', fontsize=16, fontweight='bold')
    
    colors = ['blue', 'red', 'green']
    
    for i, (case_name, material_label) in enumerate(material_cases):
        case_data = df[df['case_name'] == case_name].copy()
        
        if case_data.empty:
            print(f"Warning: No data found for case {case_name}")
            continue
        
        # Sort by volume
        case_data = case_data.sort_values('volume')
        color = colors[i % len(colors)]
        
        # Plot circumferential strain
        ax1.plot(case_data['volume'], case_data['circumferential_strain'], 
                color=color, linewidth=2, label=material_label)
        
        # Plot longitudinal strain
        ax2.plot(case_data['volume'], case_data['longitudinal_strain'], 
                color=color, linewidth=2, label=material_label)
        
        # Plot twist angle
        ax3.plot(case_data['volume'], case_data['twist_angle'], 
                color=color, linewidth=2, label=material_label)
    
    # Set labels and formatting
    ax1.set_ylabel('Circumferential Strain', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(title='Material', fontsize=10)
    ax1.set_title('Circumferential Strain vs Volume', fontsize=14)
    
    ax2.set_ylabel('Longitudinal Strain', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(title='Material', fontsize=10)
    ax2.set_title('Longitudinal Strain vs Volume', fontsize=14)
    
    ax3.set_xlabel('Volume', fontsize=12)
    ax3.set_ylabel('Twist Angle', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(title='Material', fontsize=10)
    ax3.set_title('Twist Angle vs Volume', fontsize=14)
    
    plt.tight_layout()
    
    # Save plot
    output_file = plots_dir / "material_comparison_8_30_0circ.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved material comparison plot: {output_file}")


def main():
    """Main function to create all plots."""
    
    parser = argparse.ArgumentParser(
        description="Create plots from ventricle analysis results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 make_plots.py
    python3 make_plots.py ventricle_analysis_results.csv
        """
    )
    
    parser.add_argument(
        'csv_file', 
        nargs='?', 
        default='ventricle_analysis_results.csv',
        help='Input CSV file (default: ventricle_analysis_results.csv)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found.")
        sys.exit(1)
    
    print(f"Loading data from: {args.csv_file}")
    
    try:
        # Load the CSV file
        df = pd.read_csv(args.csv_file)
        print(f"Loaded {len(df)} rows from CSV file")
        
        # Create plots directory
        plots_dir = create_plots_directory()
        print(f"Created/using plots directory: {plots_dir}")
        
        # Get unique case names
        case_names = df['case_name'].unique()
        print(f"Found {len(case_names)} unique cases: {sorted(case_names)}")
        
        # 1. Create individual plots for each case
        print("\n1. Creating individual plots for each case...")
        for case_name in case_names:
            plot_individual_case(df, case_name, plots_dir)
        
        # 2. Create comparison plots
        print("\n2. Creating comparison plots...")
        
        # 8_30_0circ vs 8_30_2circ
        plot_case_comparison(
            df, 
            ['8_30_0circ', '8_30_2circ'], 
            'Comparison: 8_30_0circ vs 8_30_2circ',
            'comparison_8_30_0circ_vs_2circ.png',
            plots_dir
        )
        
        # 8_30_0circ, 10_30_0circ, 12_30_0circ
        plot_case_comparison(
            df, 
            ['8_30_0circ', '10_30_0circ', '12_30_0circ'], 
            'Comparison: Different Helix Numbers (0circ)',
            'comparison_helix_numbers_0circ.png',
            plots_dir
        )
        
        # 8_30_2circ, 10_30_2circ, 12_30_2circ
        plot_case_comparison(
            df, 
            ['8_30_2circ', '10_30_2circ', '12_30_2circ'], 
            'Comparison: Different Helix Numbers (2circ)',
            'comparison_helix_numbers_2circ.png',
            plots_dir
        )
        
        # 3. Create helix angle comparison plots
        print("\n3. Creating helix angle comparison plots...")
        
        helix_angles = ['20', '25', '30', '35', '40']
        
        # 8_{helix_angle}_0circ
        plot_helix_angle_comparison(df, helix_angles, '0circ', plots_dir)
        
        # 8_{helix_angle}_2circ
        plot_helix_angle_comparison(df, helix_angles, '2circ', plots_dir)
        
        # 4. Create material comparison plot
        print("\n4. Creating material comparison plot...")
        plot_material_comparison(df, plots_dir)
        
        print(f"\nAll plots completed successfully!")
        print(f"Plots saved in directory: {plots_dir.absolute()}")
        
        # List all created files
        plot_files = list(plots_dir.glob("*.png"))
        print(f"Created {len(plot_files)} plot files:")
        for file in sorted(plot_files):
            print(f"  - {file.name}")
        
    except Exception as e:
        print(f"Error creating plots: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
