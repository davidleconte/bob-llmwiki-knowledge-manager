---
slug: track-compliance
name: Compliance Tracking
description: Manage regulatory obligations, track deadlines, collect evidence, and generate compliance reports in IBM OpenPages.
category: product
tags:
  - GRC
  - Compliance
  - OpenPages
  - Regulatory
related_modes:
  - openpages
  - governance
  - devsecops
---

# Compliance Tracking

A skill for managing the full regulatory compliance lifecycle in IBM OpenPages — from obligation mapping to evidence collection and report generation.

## Included capabilities

### Regulatory Frameworks Supported
- **SOX**: Sections 302/404, ICFR controls, CEO/CFO certification workflows
- **GDPR**: Data subject rights, processing records (ROPA), DPIAs, breach notification
- **HIPAA**: Security Rule (§ 164.312), Privacy Rule, and BAA management
- **ISO 27001**: Annex A control mapping, ISMS scope, and certification readiness
- **PCI-DSS**: 12 requirements, SAQ types, and cardholder data environment scoping

### Obligation Management
- Create and categorize regulatory obligations via `op_create_object`
- Map obligations to business processes, systems, and data assets
- Owner assignment with acceptance workflows
- Obligation decomposition: regulation → requirement → control → evidence

### Deadline Tracking
- Compliance calendar: assessment deadlines, submission dates, certification renewals
- Upcoming deadline queries: obligations due within configurable windows
- Overdue obligation alerts: escalation to compliance officers
- Regulatory change tracking: amendment date capture and impact assessment

### Evidence Collection
- Evidence record creation: document upload references, test results, attestations
- Evidence validity windows: define how long evidence remains current
- Evidence gap analysis: obligations without supporting evidence
- Bulk evidence request generation for annual assessment cycles

### Compliance Assessment Workflows
1. **Scoping**: identify which regulations apply to which business units/systems
2. **Gap Analysis**: `op_query` to find requirements without adequate controls
3. **Testing**: create test records, link to control population
4. **Sign-Off**: workflow routing to control owners and management
5. **Reporting**: aggregate status by regulation, business unit, or control family

### Report Generation
- Compliance status dashboard: % compliant by regulation and business unit
- Outstanding obligations report: overdue, due soon, and unassigned
- Evidence sufficiency report: gaps requiring remediation
- Regulatory submission readiness: certification checklist format

## Usage

Install this skill with:

```bash
bobmodes install-skill track-compliance
```

Project installs are copied into:

```text
<install-path>/
```

## Example prompt

> "Show me all GDPR obligations that are overdue or have no evidence attached, grouped by data processing activity."

Bob will query OpenPages via MCP tools and produce a structured gap report with owner details and remediation priorities.
