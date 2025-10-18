#!/bin/bash

# Name of your job
#SBATCH --job-name=jobname

# Name of partition
#SBATCH --partition=amarsden

# Specify the name of the output file. The %j specifies the job ID
#SBATCH --output=job.o%j

# Specify a name of the error file. The %j specifies the job ID
#SBATCH --error=job.e%j

# The walltime you require for your simulation
#SBATCH --time=6:00:00

# Job priority. Leave as normal for now.
#SBATCH --qos=normal

# Number of nodes you are requesting for your job. You can have 16 processors per node, so plan accordingly
#SBATCH --nodes=1

# Amount of memory you require per node. The default is 4000 MB (or 4 GB) per node
#SBATCH --mem=20000

# Number of processors per node
#SBATCH --ntasks-per-node=24

# Send an email to this address when you job starts and finishes
#SBATCH --mail-user=dseyler@stanford.edu
#SBATCH --mail-type=begin
#SBATCH --mail-type=fail
#SBATCH --mail-type=end

# Clean simulation directory
make clean

module purge
# for process_results.py
module load viz
module load py-matplotlib/3.8.3_py312
module load py-scipy/1.12.0_py312
module load py-seaborn/0.13.2_py312

python3 -u ../generate_pressure.py

MESH_DIR="meshes/ventricle_8_35_c-mesh-complete"
PRESSURE_FILE="pressure.dat"

echo "Processing $MESH_DIR with $PRESSURE_FILE"
python3 -u ../edit_solver.py solver.xml $MESH_DIR 0.001 1000 --pressure-file $PRESSURE_FILE

# Start Volume watcher: terminate if volume exceeds 2.0x undeformed volume
rm -f .volume_exceeded 2>/dev/null || true
# Volume watcher logs per-case volumes to a dedicated log file
vol_log="volume_8_35_2circ.log"
python3 -u ../watchers.py volume --ref-surface "$MESH_DIR/mesh-surfaces/epi.vtp" \
                                  --results-glob "results_ventricle_8_35_c*" --threshold-factor 2.0 \
                                  --marker .volume_exceeded --log-file "$vol_log" --kill-on-exceed &
VOL_WATCHER_PID=$!

# MPI run the executable svFSI with svFSI.xml
singularity exec /home/groups/amarsden/svMultiPhysics/solver_latest.sif bash -c "mpirun -n 24 $HOME/solver/svMultiPhysics/build/svMultiPhysics-build/bin/svmultiphysics solver.xml"

# Ensure watcher is stopped after solver exits
kill $VOL_WATCHER_PID 2>/dev/null || true

# If volume exceeded detected, stop simulation
if [ -f .volume_exceeded ]; then
    echo "Stopping simulation due to volume threshold exceeded for $MESH_DIR with $PRESSURE_FILE"
    rm -f .volume_exceeded
fi


# Submit job with 
# sbatch ./svFSI_job.sh
# Check status with
# squeue -u $USER
