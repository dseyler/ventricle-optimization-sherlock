#!/usr/bin/env python3
"""
Comprehensive analysis script for ventricle optimization simulations.

This script analyzes all simulation results in the Sherlock_jobs directory and generates:
1. A CSV file with twist angles, strains, and volumes for each case and time step
2. Principal strain VTP meshes saved in each case directory

Author: Assistant
Date: 2024
"""

import os
import sys
import glob
import numpy as np
import pandas as pd
import pyvista as pv
import multiprocessing as mp
from functools import partial
import argparse
from process_results_functions import (
    calc_twist_angle, 
    calc_volume_3D,
    get_start_end_step
)

def find_results_directories(base_dir):
    """Find all results directories in the Sherlock_jobs structure."""
    results_dirs = []
    case_dirs = glob.glob(os.path.join(base_dir, "*_*_*circ"))
    
    for case_dir in case_dirs:
        case_name = os.path.basename(case_dir)
        # Look for results directories in the case folder
        results_pattern = os.path.join(case_dir, "results*")
        case_results = glob.glob(results_pattern)
        
        if case_results:
            # Should be only one results directory per case
            results_dirs.append({
                'case_name': case_name,
                'case_dir': case_dir,
                'results_dir': case_results[0]
            })
    
    return results_dirs

def calculate_principal_strains(mesh, ref_lumen, timestep):
    """
    Calculate principal strains using the same method as analyze_twist_angles.py
    
    Args:
        mesh: PyVista mesh with Def_grad tensor
        ref_lumen: Reference lumen surface for sampling
        timestep: Current time step number
        
    Returns:
        dict with strain information
    """
    try:
        # Ensure Def_grad is point data
        has_point = ('Def_grad' in mesh.point_data)
        has_cell = ('Def_grad' in mesh.cell_data)
        if not has_point and has_cell:
            try:
                mesh = mesh.cell_data_to_point_data(pass_cell_data=True)
            except Exception:
                pass
        
        # Sample result onto reference lumen and warp by displacement
        resampled = ref_lumen.sample(mesh)
        warped = resampled.warp_by_vector('Displacement')
        
        # Compute principal Green-Lagrange strain (max) and direction at each point
        if 'Def_grad' not in resampled.point_data:
            return {'mesh_with_strains': None}
        
        F_flat = np.asarray(resampled.point_data['Def_grad'])  # shape (N, 9)
        if F_flat.ndim != 2 or F_flat.shape[1] != 9:
            return {'mesh_with_strains': None}
        
        # Reshape to (N, 3, 3)
        F = F_flat.reshape((-1, 3, 3))
        # Right Cauchy-Green tensor C = F^T F
        C = np.einsum('...ji,...jk->...ik', F, F)
        # Eigen-decomposition of C
        # For numerical stability, symmetrize C
        C_sym = 0.5 * (C + np.swapaxes(C, -1, -2))
        # Use numpy.linalg.eigh which assumes symmetric input
        vals, vecs = np.linalg.eigh(C_sym)  # vals ascending per point
        # Principal Green-Lagrange strains: E_i = 0.5*(lambda_i - 1), where lambda_i are eigenvalues of C
        E_principal = 0.5 * (vals - 1.0)
        
        # Get all three principal strains (sorted in descending order)
        E_principal_sorted = np.sort(E_principal, axis=1)[:, ::-1]  # Descending order
        
        # Take max principal strain and corresponding direction
        max_idx = np.argmax(E_principal, axis=1)
        max_strain = E_principal[np.arange(E_principal.shape[0]), max_idx]
        
        # Directions: eigenvectors in reference configuration
        dirs = np.zeros_like(vecs)
        for i in range(vecs.shape[0]):
            dirs[i] = vecs[i]
        max_dir = dirs[np.arange(dirs.shape[0]), :, max_idx]
        # Normalize direction vectors
        norms = np.linalg.norm(max_dir, axis=1, keepdims=True) + 1e-12
        max_dir_unit = max_dir / norms
        
        # Attach fields to warped surface (current configuration geometry)
        warped.point_data['MaxPrincipalStrain'] = max_strain.astype(np.float64)
        warped.point_data['MaxPrincipalStrainDir'] = max_dir_unit.astype(np.float64)
        warped.point_data['PrincipalStrain_1'] = E_principal_sorted[:, 0].astype(np.float64)
        warped.point_data['PrincipalStrain_2'] = E_principal_sorted[:, 1].astype(np.float64)
        warped.point_data['PrincipalStrain_3'] = E_principal_sorted[:, 2].astype(np.float64)
        
        # Displacement should already exist; ensure present
        if 'Displacement' in resampled.point_data and 'Displacement' not in warped.point_data:
            warped.point_data['Displacement'] = np.asarray(resampled.point_data['Displacement'])
        
        return {
            'mesh_with_strains': warped,
            'principal_strains': E_principal_sorted
        }
        
    except Exception as e:
        print(f"Error calculating principal strains for timestep {timestep}: {e}")
        return {'mesh_with_strains': None}

def analyze_single_case(case_info):
    """
    Analyze a single simulation case.
    
    Args:
        case_info: Dictionary with case_name, case_dir, and results_dir
        
    Returns:
        DataFrame with analysis results
    """
    case_name = case_info['case_name']
    case_dir = case_info['case_dir']
    results_dir = case_info['results_dir']
    
    print(f"Analyzing case: {case_name}")
    
    # Find reference surface (epi.vtp)
    ref_surface_pattern = os.path.join(case_dir, "meshes", "*", "mesh-surfaces", "epi.vtp")
    ref_surfaces = glob.glob(ref_surface_pattern)
    
    if not ref_surfaces:
        print(f"Warning: No reference surface found for {case_name}")
        return pd.DataFrame()
    
    ref_surface = ref_surfaces[0]
    
    # Get simulation parameters
    try:
        start_step, end_step, step = get_start_end_step(results_dir)
        timestep_size = 0.001
    except Exception as e:
        print(f"Error getting simulation parameters for {case_name}: {e}")
        return pd.DataFrame()
    
    # Calculate twist angles
    print(f"  Calculating twist angles...")
    try:
        # calc_twist_angle returns (time_array, twist_angles_dict, z_levels)
        time_array, twist_angles_by_z, z_levels_used = calc_twist_angle(
            start_step, end_step, step, timestep_size, 
            results_dir, ref_surface, 
            save_intermediate_data=False
        )
        
        # Generate time steps from the time array
        time_steps = [int(t / timestep_size) for t in time_array]
        
        # Calculate twist angle as difference between max and min z-level twist angles
        twist_angle_differences = []
        for t_idx in range(len(time_array)):
            z_twist_angles = [twist_angles_by_z[z_level][t_idx] for z_level in z_levels_used]
            twist_diff = max(z_twist_angles) - min(z_twist_angles)
            twist_angle_differences.append(twist_diff)
            
    except Exception as e:
        print(f"Error calculating twist angles for {case_name}: {e}")
        # Need to still define time_steps for later use
        time_steps = list(range(start_step, end_step + 1, step))
        twist_angle_differences = [np.nan] * len(time_steps)
    
    # Calculate volumes and strains using calc_volume_3D function
    print(f"  Calculating volumes and strains...")
    try:
        volume_results = calc_volume_3D(
            start_step, end_step, step, timestep_size,
            results_dir, ref_surface,
            save_intermediate_data=False
        )
        volumes = volume_results['volumes']
        radial_strains = volume_results['radial_strains']  # Same as circumferential
        longitudinal_strains = volume_results['longitudinal_strains']
        
        # Use radial_strains as circumferential_strains (they are the same)
        circumferential_strains = radial_strains
        
    except Exception as e:
        print(f"Error calculating volumes and strains for {case_name}: {e}")
        volumes = [np.nan] * len(time_steps)
        circumferential_strains = [np.nan] * len(time_steps)
        longitudinal_strains = [np.nan] * len(time_steps)
    
    # Prepare reference lumen once for consistent sampling
    print(f"  Preparing reference lumen for strain calculation...")
    try:
        ref_surf_full = pv.read(ref_surface)
        ref_lumen = ref_surf_full.fill_holes(100)
        ref_lumen.compute_normals(inplace=True)
    except Exception as e:
        print(f"Error preparing reference lumen for {case_name}: {e}")
        ref_lumen = None
    
    # Save principal strain meshes for every 10th timestep
    print(f"  Saving principal strain meshes...")
    if ref_lumen is None:
        print(f"  Warning: ref_lumen is None, skipping principal strain mesh creation")
    else:
        print(f"  ref_lumen created successfully, processing {len(time_steps)} timesteps")
        
    files_saved = 0
    for t_idx, time_step in enumerate(time_steps):
        if time_step % 1 == 0:  # Save every timestep
            try:
                # Load the VTU file for this timestep
                vtu_file = os.path.join(results_dir, f"result_{time_step:06d}.vtu")
                if os.path.exists(vtu_file):
                    if ref_lumen is not None:
                        mesh = pv.read(vtu_file)
                        strain_info = calculate_principal_strains(mesh, ref_lumen, time_step)
                        
                        # Save principal strain mesh if calculation was successful
                        if strain_info.get('mesh_with_strains') is not None:
                            strain_mesh = strain_info['mesh_with_strains']
                            strain_output_file = os.path.join(case_dir, f"principal_strain_{time_step:06d}.vtp")
                            strain_mesh.save(strain_output_file)
                            files_saved += 1
                            if files_saved <= 3:  # Only print first few for debugging
                                print(f"    Saved: {strain_output_file}")
                        else:
                            print(f"    Warning: No strain mesh created for timestep {time_step}")
                    else:
                        print(f"    Skipping timestep {time_step}: ref_lumen is None")
                else:
                    print(f"    Warning: VTU file not found: {vtu_file}")
                        
            except Exception as e:
                print(f"    Error saving principal strain mesh for timestep {time_step}: {e}")
    
    print(f"  Total principal strain files saved: {files_saved}")
    
    # Create DataFrame for this case
    case_data = pd.DataFrame({
        'case_name': [case_name] * len(time_steps),
        'time_step': time_steps,
        'time': [t * timestep_size for t in time_steps],
        'twist_angle': twist_angle_differences,
        'circumferential_strain': circumferential_strains,
        'longitudinal_strain': longitudinal_strains,
        'volume': volumes
    })
    
    print(f"  Completed analysis for {case_name}")
    return case_data

def main():
    """Main analysis function with parallel processing."""
    
    parser = argparse.ArgumentParser(description='Analyze ventricle simulation results')
    parser.add_argument('--n-processes', type=int, default=None, 
                       help='Number of parallel processes (default: number of CPU cores)')
    parser.add_argument('--base-dir', type=str, default=None,
                       help='Base directory to analyze (default: script directory)')
    parser.add_argument('--output-file', type=str, default='ventricle_analysis_results.csv',
                       help='Output CSV file name')
    args = parser.parse_args()
    
    # Get the script directory (Sherlock_jobs) or use provided base directory
    if args.base_dir:
        script_dir = args.base_dir
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set number of processes
    n_processes = args.n_processes if args.n_processes else mp.cpu_count()
    
    print("Starting comprehensive analysis of ventricle simulations...")
    print(f"Base directory: {script_dir}")
    print(f"Using {n_processes} parallel processes")
    
    # Find all results directories
    results_dirs = find_results_directories(script_dir)
    
    if not results_dirs:
        print("No results directories found!")
        return
    
    print(f"Found {len(results_dirs)} cases to analyze:")
    for case in results_dirs:
        print(f"  - {case['case_name']}")
    
    # Process cases in parallel
    print(f"\nProcessing {len(results_dirs)} cases using {n_processes} processes...")
    
    # Create a partial function with fixed arguments for multiprocessing
    analyze_func = partial(analyze_single_case)
    
    # Use multiprocessing to analyze cases in parallel
    with mp.Pool(processes=n_processes) as pool:
        results = pool.map(analyze_func, results_dirs)
    
    # Filter out empty results
    all_data = [data for data in results if not data.empty]
    
    if not all_data:
        print("No data collected from any cases!")
        return
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Save to CSV
    output_file = os.path.join(script_dir, args.output_file)
    combined_data.to_csv(output_file, index=False)
    
    print(f"\nAnalysis complete!")
    print(f"Results saved to: {output_file}")
    print(f"Total data points: {len(combined_data)}")
    print(f"Cases analyzed: {combined_data['case_name'].nunique()}")
    
    # Print summary statistics
    print("\nSummary statistics:")
    print("==================")
    for case in combined_data['case_name'].unique():
        case_data = combined_data[combined_data['case_name'] == case]
        print(f"\n{case}:")
        print(f"  Time steps: {len(case_data)}")
        if not case_data['twist_angle'].isna().all():
            print(f"  Twist angle range: {case_data['twist_angle'].min():.3f} to {case_data['twist_angle'].max():.3f}")
        if not case_data['circumferential_strain'].isna().all():
            print(f"  Circumferential strain range: {case_data['circumferential_strain'].min():.3f} to {case_data['circumferential_strain'].max():.3f}")
        if not case_data['longitudinal_strain'].isna().all():
            print(f"  Longitudinal strain range: {case_data['longitudinal_strain'].min():.3f} to {case_data['longitudinal_strain'].max():.3f}")
        if not case_data['volume'].isna().all():
            print(f"  Volume range: {case_data['volume'].min():.6f} to {case_data['volume'].max():.6f}")

if __name__ == "__main__":
    # Required for multiprocessing on some systems
    mp.set_start_method('spawn', force=True)
    main()
