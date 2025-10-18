#!/bin/bash

# SLURM job script for running comprehensive ventricle analysis
#SBATCH --job-name=ventricle_analysis

# Name of partition
#SBATCH --partition=amarsden

# Specify the name of the output file. The %j specifies the job ID
#SBATCH --output=analysis_job.o%j

# Specify a name of the error file. The %j specifies the job ID
#SBATCH --error=analysis_job.e%j

# The walltime you require for your analysis
#SBATCH --time=04:00:00

# Job priority. Leave as normal for now.
#SBATCH --qos=normal

# Number of nodes you are requesting for your job
#SBATCH --nodes=1

# Amount of memory you require per node
#SBATCH --mem=32000

# Number of processors per node (use all cores for parallel processing)
#SBATCH --ntasks-per-node=32

# Send an email to this address when you job starts and finishes
#SBATCH --mail-user=dseyler@stanford.edu
#SBATCH --mail-type=begin
#SBATCH --mail-type=fail
#SBATCH --mail-type=end

echo "Starting ventricle analysis job..."
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Start time: $(date)"

# Load required modules
module purge
module load viz
module load py-matplotlib/3.8.3_py312
module load py-scipy/1.12.0_py312
module load py-seaborn/0.13.2_py312
module load py-pandas/2.2.1_py312

echo "Modules loaded successfully"

# Set up environment
export OMP_NUM_THREADS=1  # Prevent OpenMP conflicts with multiprocessing
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Get the number of available CPU cores
N_CORES=$SLURM_CPUS_ON_NODE
echo "Available CPU cores: $N_CORES"

# Run the analysis script with parallel processing
echo "Running comprehensive ventricle analysis..."
echo "Using $N_CORES processes for parallel analysis"

# Run the analysis script
python3 analyze_data.py --n-processes $N_CORES

# Check if the analysis completed successfully
if [ $? -eq 0 ]; then
    echo "Analysis completed successfully!"
    echo "Results saved to ventricle_analysis_results.csv"
    
    # Show file size and basic info
    if [ -f "ventricle_analysis_results.csv" ]; then
        echo "Output file info:"
        ls -lh ventricle_analysis_results.csv
        echo "Number of lines in results file:"
        wc -l ventricle_analysis_results.csv
    fi
    
    # Show summary of results directories created
    echo "Principal strain meshes created in case directories:"
    find . -name "principal_strains_*.vtp" | wc -l | xargs echo "Total principal strain mesh files:"
    
else
    echo "Analysis failed with exit code $?"
    exit 1
fi

echo "Job completed at: $(date)"
