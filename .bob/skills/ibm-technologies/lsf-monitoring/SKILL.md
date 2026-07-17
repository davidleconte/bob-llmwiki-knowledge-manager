---
slug: lsf-monitoring
name: LSF Cluster Monitoring
description: Cluster health checks, job tracking, queue analysis, and load monitoring for IBM Platform LSF.
category: product
tags:
  - HPC
  - LSF
  - Monitoring
  - Operations
related_modes:
  - ibm-lsf
  - sre
  - aiops-rca-analyst
---

# LSF Cluster Monitoring

A skill for comprehensive IBM Platform LSF cluster health monitoring, job status tracking, and operational visibility.

## Included capabilities

### Cluster Health Commands
- `bhosts` / `bhosts -l <host>` — host slot availability, load indices, and status
- `bqueues` / `bqueues -l <queue>` — queue configuration, limits, and current occupancy
- `lsload` — real-time host load: CPU, memory, I/O, and custom resources
- `lshosts` — static host configuration: CPUs, sockets, cores, memory, and resources
- `bgpustat` — GPU utilization and allocation status per host

### Job Status Tracking
- `bjobs` — all running and pending jobs with status, queue, host assignment
- `bjobs -u <user>` — per-user job view
- `bjobs -q <queue>` — per-queue job view
- `bjobs -p` — pending jobs with PEND_REASON detail
- `bjobs -A` — job array element status summary
- `bjobs -l <jobid>` — full job detail: resources, start time, predicted end

### Historical Analysis
- `bhist <jobid>` — job lifecycle events and resource consumption
- `bhist -l <jobid>` — verbose history with scheduling events
- `bacct -l <jobid>` — detailed accounting: CPU, memory, swap used
- Batch efficiency calculations: CPU time / wall time × slots

### Health Check Workflows
1. Check all hosts up: `bhosts | grep -v ok`
2. Check queue lengths: `bqueues | awk '{print $1,$8,$9}'`
3. Check PEND reasons: `bjobs -p | sort -k5 | uniq -c`
4. Check GPU availability: `bgpustat`
5. Load overview: `lsload -l`

### Alerting Thresholds
- Job queue depth > N: flag for capacity review
- Host DOWN status: immediate escalation
- PEND_REASON `LOAD` for > 30 min: resource contention signal
- Job EXIT rate > 10%: environment or configuration issue indicator

## Usage

Install this skill with:

```bash
bobmodes install-skill lsf-monitoring
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Run a full cluster health check and tell me if any jobs have been pending for more than 2 hours."

Bob will execute the health check sequence, parse the output, and provide a structured health report with actionable findings.
