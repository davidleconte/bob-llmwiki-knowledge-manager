---
slug: audit-controls
name: Control Auditing
description: Test control design and operating effectiveness, document deficiencies, track remediation, and prepare for SOX 404 and IT General Controls audits in IBM OpenPages.
category: product
tags:
  - GRC
  - Audit
  - OpenPages
  - SOX
  - Controls
related_modes:
  - openpages
  - governance
  - devsecops
---

# Control Auditing

A skill for systematic internal control auditing in IBM OpenPages — from test planning through deficiency classification and remediation tracking.

## Included capabilities

### Control Universe Management
- Query control population: `op_query` by control category, owner, or risk linkage
- Control classification: IT General Controls (ITGC), Application Controls, Business Process Controls
- Control design assessment: evaluating whether the control design can prevent/detect the risk
- Control frequency mapping: continuous, daily, weekly, monthly, quarterly, annual

### Test Planning
- Walkthroughs: narrative documentation of control design and process flow
- Sample selection guidance: statistical and judgmental sampling for control testing
- Test program creation: step-by-step test procedures linked to control attributes
- Test scheduling: assign testers, set start/end dates, and track completion

### Testing Execution
- Test result recording: Effective / Ineffective / Not Tested
- Evidence attachment references: test workpaper links, screenshots, exports
- Exception documentation: describe deviations observed during testing
- Re-testing: after remediation, schedule and record retest results

### Deficiency Classification
Three-tier classification with specific criteria:

| Classification | Criteria | Required Response |
|---|---|---|
| **Control Deficiency** | Design or operation gap that could allow misstatement | Remediate within normal cycle |
| **Significant Deficiency** | Less severe than material weakness; warrants attention | Communicate to audit committee; remediate urgently |
| **Material Weakness** | Reasonable possibility of material misstatement | Disclose in SOX 302/404; immediate remediation required |

### Remediation Tracking
- Create remediation action items linked to deficiencies
- Assign remediation owners and target completion dates
- Track remediation status: Open → In Progress → Completed → Validated
- Validate remediation: confirm deficiency resolved before closing
- Root cause categorization: process design, human error, system, or oversight failure

### SOX 404 Readiness
- ICFR scoping: identify significant accounts and processes
- Entity-Level Controls (ELC) assessment framework
- IT General Controls testing: access management, change management, operations
- Management assessment documentation: certifiable evidence package
- Deficiency aggregation: assess combined impact of multiple deficiencies

### Audit Report Generation
- Control testing summary: tested population, results, and exception rate
- Deficiency register: all findings with classification, owner, and status
- Management action plan: remediation commitments with deadlines
- Audit opinion support: evidence package for external auditors

## Usage

Install this skill with:

```bash
bobmodes install-skill audit-controls
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "List all IT General Controls that tested ineffective this period and classify any significant deficiencies. Generate a management action plan."

Bob will query OpenPages for failed ITGC tests, apply deficiency classification logic, and produce a structured management action plan with owner assignments and remediation dates.
