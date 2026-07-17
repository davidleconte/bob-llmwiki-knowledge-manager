---
slug: lsf-job-submission
name: LSF Job Submission
description: bsub script patterns for serial, MPI, OpenMP, GPU, and job array workloads on IBM Platform LSF.
category: product
tags:
  - HPC
  - LSF
  - Job Scheduling
  - Parallel Computing
related_modes:
  - ibm-lsf
  - sre
  - kubernetes
---

# LSF Job Submission

A comprehensive skill for writing correct, production-annotated IBM Platform LSF job scripts for every workload type.

## Included capabilities

### Mandatory bsub Directives
Every generated script includes the full set of required directives:
- `-J <jobname>` — descriptive job name
- `-q <queue>` — target queue
- `-n <slots>` — CPU slot count
- `-W <HH:MM>` — wall-clock time limit
- `-R "rusage[mem=N]"` — memory reservation in MB
- `-o <log>/%J.out` — stdout with job ID in filename
- `-e <log>/%J.err` — stderr with job ID in filename

### Serial Job Patterns
- Single-core batch jobs with explicit memory limits
- Array job variants using `$LSB_JOBINDEX` for parameter sweeps
- Job dependency chains: `#BSUB -w "done(jobname)"`

### Parallel Job Patterns
- **MPI jobs**: `span[ptile=N]` for processes-per-node, `mpirun`/`mpiexec` launch lines
- **OpenMP jobs**: `OMP_NUM_THREADS` export, single-node affinity via `span[hosts=1]`
- **Hybrid MPI/OpenMP**: combined `span[ptile=N]` with `OMP_NUM_THREADS` configuration
- **GPU jobs**: `-gpu "num=N:mode=exclusive_process:j_exclusive=yes"` with CUDA environment setup

### Job Array Patterns
- Array submission: `-J "name[1-N]"` with optional step and concurrency limit (`%M`)
- `$LSB_JOBINDEX` usage for input file selection and output naming
- Array status: `bjobs -A` for element-level monitoring

### Environment & Module Handling
- `module load` integration for software environment setup
- Environment variable export before `mpirun`/`srun`
- Working directory management: `cd $LS_SUBCWD`

## Usage

Install this skill with:

```bash
bobmodes install-skill lsf-job-submission
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Write an LSF job script that runs a 64-process MPI job using 8 processes per node, 4 hours wall time, 4GB memory per slot, on the `parallel` queue."

Bob will generate a complete, annotated bsub script with all mandatory directives, correct `span[ptile=8]`, and `mpirun` invocation.
