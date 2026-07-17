# AI Pilot Risk Assessment Skill

A Bob skill that guides you through a structured risk analysis for AI pilot projects and Proofs of Concept (PoCs).

## What It Does

When you are planning, evaluating, or documenting an AI pilot — especially one using IBM watsonx or similar AI platforms — this skill surfaces the most common failure patterns early, before they become blockers. It maps every finding to the **IBM Client Engineering (CE)** methodology and phase gates (Discover → Envision → Empower).

## When to Use It

Activate this skill by asking questions such as:

- *"What can go wrong in our AI pilot?"*
- *"Help me de-risk this PoC."*
- *"Review our pilot project for risks."*
- *"We're planning an AI pilot — what should we watch out for?"*

## What You Get

The skill walks through **six structured steps**:

| Step | Output |
|------|--------|
| 1 · Understand the Context | Project goals, CE phase, stakeholders, maturity level |
| 1b · As-Is Process & Systems | Current process description, backend system inventory, integration checklist |
| 1c · Delta Analysis | Gap table comparing As-Is vs. To-Be across process, data, roles, compliance, and infrastructure |
| 2 · 15-Question Risk Checklist | Covers resources, product knowledge, technology, and budget |
| 3 · Risk List | Up to 20 named risks split into **Delivery (RD)** and **Technical (RT)** categories with probability, impact, score, owner, and CE phase gate |
| 4 · Open Items | Eight pilot-specific clarification questions (OP-P01 – OP-P08) |
| 5 · Document Output | Extends existing project files or creates a standalone risk document |
| 6 · Immediate Actions | Prioritised list of blockers per CE phase gate |

## Key Risk Categories

| Category | Examples |
|----------|----------|
| **Delivery (RD)** | Missing sponsor, no rollout budget, uncommitted customer resources, unclear ownership |
| **Technical (RT)** | Sandbox data ≠ production data, no API access to source systems, GDPR / EU AI Act gaps, infrastructure not budgeted |

## IBM CE Alignment

Every finding is framed against the three CE phase gates:

- **Discover → Envision:** Problem statement validated, success criteria defined
- **Envision → Empower:** Go/No-Go criteria documented, architecture sketch agreed
- **Empower → Production:** PoC runs on real data, scale-up roadmap approved

> A pilot without a visible path to production value is a science experiment, not a business engagement.

## Guiding Principle

**Organisation-First, not Tool-First** — technology follows the business need. Up to 95 % of AI pilots never reach production; this skill exists to put yours in the other 5 %.
