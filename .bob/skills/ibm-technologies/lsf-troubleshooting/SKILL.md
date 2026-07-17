---
slug: lsf-troubleshooting
name: LSF Job Troubleshooting
description: Diagnose and resolve PEND reasons, EXIT failures, resource mismatches, and scheduling issues on IBM Platform LSF.
category: product
tags:
  - HPC
  - LSF
  - Troubleshooting
  - Debugging
related_modes:
  - ibm-lsf
  - sre
---

# LSF Job Troubleshooting

A skill for systematic diagnosis and resolution of IBM Platform LSF job failures, pending states, and scheduling anomalies.

## Included capabilities

### PEND Reason Diagnosis
Each PEND reason is mapped to a diagnostic and remediation path:

| PEND Reason | Diagnosis | Fix |
|---|---|---|
| `Not enough job slot(s)` | Queue/host slot limit reached | Check `bqueues -l`, increase SLOTS or wait |
| `Not enough memory` | rusage[mem=N] exceeds free memory | Reduce `-R "rusage[mem=N]"` or wait for slots |
| `Job's requirement for resource not satisfied` | Custom resource unavailable | Verify resource string with `lshosts -R` |
| `Queue does not have enough host(s)` | No hosts in queue match constraints | Check `-R` string vs. `bhosts -R` |
| `Job's requirements not met` | Slot/span constraint impossible | Review `span[ptile=N]` vs. host slot count |
| `Load threshold reached` | Host load too high | Check `lsload`; wait or redirect to other queue |

### EXIT Code Analysis
- Exit code 1: application error — check job stderr with `cat <job>.err`
- Exit code 127: command not found — check `module load` or PATH in script
- Exit code 130/131: job killed (SIGINT/SIGQUIT) — check wall time or manual kill
- Exit code 137: OOM kill — increase `rusage[mem=N]` or check for memory leak
- Non-zero bsub: submission error — check syntax with `bsub -q <q> -n 1 -W 1 echo test`

### Resource Mismatch Detection
- Compare requested resources in `bjobs -l` against available resources in `bhosts -l`
- Validate GPU availability: `bgpustat` vs. `-gpu "num=N"` request
- Check span constraints: requested `ptile=N` vs. actual host slot count in `bhosts`
- Verify custom resource (`bresources`) availability for named resource strings

### Recovery Procedures
- **Stuck PEND**: modify with `bmod -R "new_rusage"` to relax resource requirements
- **Wrong queue**: `bmod -q <newqueue> <jobid>` without requeueing
- **EXIT restart**: fix script, then `brequeue <jobid>` to rerun without resubmission
- **Array element failure**: `brequeue -e <jobid>[<index>]` for specific element retry

### Systematic Debug Workflow
1. `bjobs -l <jobid>` — get full resource request and PEND reason
2. `bhosts -R "<resource_string>"` — check how many hosts satisfy the request
3. `bqueues -l <queue>` — verify queue limits and current usage
4. Check job stderr: `cat <output_dir>/<jobid>.err` for application errors
5. `bhist -l <jobid>` — get scheduling event timeline

## Usage

Install this skill with:

```bash
bobmodes install-skill lsf-troubleshooting
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Job 12345 has been PEND for 3 hours with reason 'Not enough memory'. What should I do?"

Bob will walk through the diagnosis: check actual memory available, compare with requested rusage, and suggest whether to reduce the request or wait for slots to free.
