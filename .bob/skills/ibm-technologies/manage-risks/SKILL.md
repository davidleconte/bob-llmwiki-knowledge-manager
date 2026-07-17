---
slug: manage-risks
name: Risk Management
description: Complete risk lifecycle workflows for IBM OpenPages — identification, assessment, treatment planning, control linkage, and ongoing monitoring.
category: product
tags:
  - GRC
  - Risk Management
  - OpenPages
  - Compliance
related_modes:
  - openpages
  - governance
---

# Risk Management

A comprehensive skill for automating the complete risk management lifecycle in IBM OpenPages using MCP tools and structured GRC workflows.

## Included capabilities

### Risk Identification
- Create new risk records via `op_create_object` with mandatory fields: name, description, owner, risk category
- Link risks to business processes, systems, and organizational units
- Import bulk risks from spreadsheets or external sources
- Classify risks by domain: operational, financial, compliance, strategic, technology

### Risk Assessment
- Inherent risk scoring: likelihood (1–5) × impact (1–5) = inherent risk score
- Residual risk scoring: after control effectiveness applied
- Heat map positioning: High/Medium/Low categorization with threshold configuration
- Risk velocity: how quickly a risk can materialize (Immediate/Short/Medium/Long-term)
- Interdependency mapping: related risks that amplify each other

### Treatment Planning
Four treatment options with structured action plans:

| Treatment | When to Use | Required Fields |
|---|---|---|
| **Accept** | Risk within appetite; cost of control > benefit | Acceptance rationale, approver, review date |
| **Transfer** | Insurance or contract shifts risk to third party | Transfer mechanism, residual risk, coverage dates |
| **Mitigate** | Controls reduce likelihood or impact | Control description, owner, due date, KRI |
| **Avoid** | Activity discontinued to eliminate risk | Avoidance action, approval, effective date |

### Control Linkage
- Link risks to existing controls via `op_get_relationships`
- Identify control gaps: risks with no mitigating controls
- Control effectiveness rating: impacts residual risk calculation
- Control test scheduling: associate test plans with linked controls

### Ongoing Monitoring
- Key Risk Indicator (KRI) definition and threshold alerts
- Periodic risk review scheduling and owner notification
- Risk status reporting: open, in-treatment, accepted, closed
- Escalation triggers: risks exceeding appetite thresholds
- Risk trend analysis: score movement over time

## Usage

Install this skill with:

```bash
bobmodes install-skill manage-risks
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Create a new technology risk for our cloud migration project — data breach risk during migration with high likelihood and critical impact. Assign to the CISO and add a mitigate treatment plan."

Bob will create the risk record in OpenPages, score it, create the treatment plan, and assign all required fields.
