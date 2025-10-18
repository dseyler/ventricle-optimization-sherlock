#!/bin/bash

# submit_all_jobs.sh
# 
# This script submits all svFSI_job.sh files in each case directory
# It will submit jobs for all 14 cases in the Sherlock_jobs directory
#
# Usage: ./submit_all_jobs.sh
#
# The script will:
# 1. Find all case directories (pattern: *_*_*circ)
# 2. Submit the svFSI_job.sh file in each directory
# 3. Display job IDs and status
# 4. Provide commands to monitor job status

echo "=========================================="
echo "Submitting All Ventricle Simulation Jobs"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "generate_pressure.py" ]; then
    echo "Error: This script should be run from the Sherlock_jobs directory"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Array to store job IDs
declare -a job_ids=()
declare -a case_names=()

# Find all case directories
echo "Finding case directories..."
case_dirs=($(find . -maxdepth 1 -type d -name "*_*_*circ" | sort))

if [ ${#case_dirs[@]} -eq 0 ]; then
    echo "Error: No case directories found (pattern: *_*_*circ)"
    exit 1
fi

echo "Found ${#case_dirs[@]} case directories:"
for dir in "${case_dirs[@]}"; do
    echo "  - $dir"
done
echo ""

# Submit jobs
echo "Submitting jobs..."
echo "----------------------------------------"

for case_dir in "${case_dirs[@]}"; do
    case_name=$(basename "$case_dir")
    svfsi_job="$case_dir/svFSI_job.sh"
    
    if [ -f "$svfsi_job" ]; then
        echo "Submitting job for $case_name..."
        
        # Change to the case directory and submit the job
        cd "$case_dir"
        job_output=$(sbatch svFSI_job.sh 2>&1)
        
        if [ $? -eq 0 ]; then
            # Extract job ID from output (format: "Submitted batch job 12345")
            job_id=$(echo "$job_output" | grep -o '[0-9]\+')
            job_ids+=("$job_id")
            case_names+=("$case_name")
            echo "  ✓ Job submitted successfully: Job ID $job_id"
        else
            echo "  ✗ Failed to submit job for $case_name"
            echo "    Error: $job_output"
        fi
        
        # Return to parent directory
        cd ..
    else
        echo "  ✗ svFSI_job.sh not found in $case_dir"
    fi
    echo ""
done

# Summary
echo "=========================================="
echo "Job Submission Summary"
echo "=========================================="

if [ ${#job_ids[@]} -gt 0 ]; then
    echo "Successfully submitted ${#job_ids[@]} jobs:"
    echo ""
    printf "%-20s %-15s\n" "Case Name" "Job ID"
    echo "----------------------------------------"
    for i in "${!job_ids[@]}"; do
        printf "%-20s %-15s\n" "${case_names[$i]}" "${job_ids[$i]}"
    done
    echo ""
    
    echo "Useful commands to monitor your jobs:"
                     echo "----------------------------------------"
                     echo "Check job status:"
                     echo "  squeue -u \$USER"
                     echo ""
                     echo "Check specific job details:"
                     for i in "${!job_ids[@]}"; do
                         echo "  scontrol show job ${job_ids[$i]}  # ${case_names[$i]}"
                     done
                     echo ""
                     echo "Cancel all jobs (if needed):"
                     echo "  scancel ${job_ids[*]}"
                     echo ""
                     echo "Check job output files:"
                     for i in "${!job_ids[@]}"; do
                         case_dir="${case_names[$i]}"
                         echo "  $case_dir/job.o${job_ids[$i]}  # stdout"
                         echo "  $case_dir/job.e${job_ids[$i]}  # stderr"
                     done
                     echo ""
                     echo "Monitor job logs in real-time:"
                     for i in "${!job_ids[@]}"; do
                         case_dir="${case_names[$i]}"
                         echo "  tail -f $case_dir/job.o${job_ids[$i]}  # ${case_names[$i]}"
                     done
                     echo ""
                     echo "Check volume watcher logs:"
                     for i in "${!job_ids[@]}"; do
                         case_dir="${case_names[$i]}"
                         echo "  tail -f $case_dir/volume_${case_names[$i]}.log"
                     done
else
    echo "No jobs were successfully submitted."
    exit 1
fi

echo "=========================================="
echo "All jobs submitted!"
echo "=========================================="
