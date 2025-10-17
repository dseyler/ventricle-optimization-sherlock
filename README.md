# Ventricle Optimization - Sherlock Jobs

This repository contains SLURM job scripts and configuration files for running ventricle optimization simulations on Stanford's Sherlock cluster.

## Directory Structure

The repository is organized into 14 simulation cases:

## Files in Each Directory

Each case directory contains:
- `svFSI_job.sh` - SLURM job script for running the simulation
- `solver.xml` - svFSI solver configuration file
- `Makefile` - Build and cleanup commands
- `watchers.py` - Volume monitoring script
- `meshes/` - Directory containing the mesh files for the specific case

## Key Features

### Volume Monitoring
- Each simulation is monitored for volume expansion
- Simulation is automatically terminated if volume exceeds 2.5× initial volume
- Volume data is logged to case-specific log files

### Single Case Execution
- Each job runs only one simulation case
- No post-processing analysis scripts
- Clean, focused execution per parameter set

## Usage

To submit a job for a specific case:
```bash
cd 8_20_0circ  # or any other case directory
make run_sherlock
```

To check job status:
```bash
squeue -u $USER
```

## Requirements

- Stanford Sherlock cluster access
- svFSI solver (via singularity container)
- Python 3 with PyVista for volume monitoring
- SLURM job scheduler

## Configuration

### SLURM Parameters
- **Partition**: amarsden
- **Time limit**: 24 hours
- **Memory**: 20GB
- **CPUs**: 24 cores per node

### Solver Parameters
- **Time steps**: 1000
- **Time step size**: 0.001s
- **Pressure file**: pressure.dat (generated automatically)
- **Results**: Saved to case-specific directories

## Volume Monitoring

The `watchers.py` script:
1. Monitors VTU output files in real-time
2. Calculates deformed volume using PyVista
3. Compares against 2.5× initial volume threshold
4. Terminates simulation immediately when threshold exceeded
5. Logs volume data to `volume_{case_name}.log`

## File Structure

```
Sherlock_jobs/
├── README.md
├── .gitignore
├── watchers.py
├── generate_pressure.py
├── edit_solver.py
├── {case_name}/
│   ├── svFSI_job.sh
│   ├── solver.xml
│   ├── Makefile
│   ├── watchers.py
│   └── meshes/
│       └── ventricle_{a}_{b}_c-mesh-complete/
│           ├── mesh-complete.mesh.vtu
│           ├── domain_ids.dat
│           └── mesh-surfaces/
│               ├── endo.vtp
│               ├── epi.vtp
│               └── tube.vtp
```
