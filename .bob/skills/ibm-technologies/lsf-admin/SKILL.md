---
slug: lsf-admin
name: LSF Cluster Administration
description: Queue design, fairshare configuration, cluster reconfiguration, and administrative operations for IBM Platform LSF.
category: product
tags:
  - HPC
  - LSF
  - Administration
  - Configuration
related_modes:
  - ibm-lsf
  - sre
  - ansible-playbook
---

# LSF Cluster Administration

A skill for IBM Platform LSF cluster administration: queue design, fairshare policies, configuration management, and safe administrative operations.

## Included capabilities

### Queue Design
Queue definition in `lsb.queues` with these sections:
- `QUEUE_NAME`, `DESCRIPTION`, `PRIORITY` — identity and scheduling priority
- `NJOBS`, `PJOB`, `UJOB` — total, per-process, and per-user job limits
- `HOSTS` — host list or host group for queue binding
- `RES_REQ` — default resource requirements for all jobs in the queue
- `RUNTIME` — default and maximum wall-clock time
- `REQUEUE_EXIT_VALUES` — exit codes that trigger automatic requeue

### Fairshare Configuration
```
FAIRSHARE=USER_SHARES[[user1,N] [user2,N] [default,M]]
```
- User-based fairshare: relative slot share allocation
- Project-based fairshare: `USER_SHARES[[project=N]]` for project charging
- Dynamic fairshare: decays historical usage to prevent long-term starvation
- Share tree design: hierarchical groups with leaf-level users

### Pre-emption Policies
- `PREEMPTIVE=YES` — queue can preempt lower-priority jobs
- `PREEMPTABLE=YES` — queue jobs can be preempted by higher-priority queues
- Preemption actions: REQUEUE (default) or SUSPEND

### Safe Administrative Operations
⚠️ **Always validate before applying configuration changes:**

```bash
badmin ckconfig -v     # validate lsb.* config before reconfig
lsadmin ckconfig -v    # validate lsf.conf changes before apply
```

- `badmin reconfig` — apply lsb.* changes (disrupts scheduling briefly)
- `lsadmin reconfig` — apply LSF daemon config changes
- `badmin mbdrestart` — restart master batch daemon (use only when required)
- `bgadd`/`bgdel` — add/remove host groups without file editing
- `badmin hopen`/`hclose` — open/close individual hosts for scheduling

### Advance Reservation
```bash
brsvadd -n 16 -q normal -u user1 -b 2026/01/15/09:00 -e 2026/01/15/18:00 -N "reservation_name"
brsvdel <rsvid>    # delete reservation
brsvs              # list active reservations
```

### Cluster Health Administration
- License server integration: verify `lmstat -a` before scheduling license-limited jobs
- Application profile creation: `lsb.applications` for workload-specific defaults
- External scheduler hook configuration for pre/post-execution scripts

### Configuration File Reference
| File | Controls |
|---|---|
| `lsf.conf` | Master LSF daemon settings, cluster name, log dirs |
| `lsb.queues` | Queue definitions, limits, fairshare, pre-emption |
| `lsb.hosts` | Per-host job slot limits and dispatch windows |
| `lsb.resources` | Custom resource definitions |
| `lsb.applications` | Application-level job defaults |
| `lsb.groups` | User and host group definitions |

## Usage

Install this skill with:

```bash
bobmodes install-skill lsf-admin
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Design a fairshare queue for 3 research groups — genomics (50%), chemistry (30%), and physics (20%) — with a maximum of 200 concurrent jobs and 4-hour default wall time."

Bob will generate a complete `lsb.queues` stanza with correct fairshare syntax, limits, and safe validation steps before applying.
