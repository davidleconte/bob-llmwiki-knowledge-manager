# Appendix C: Template Reference

> **Live document.** This chapter is part of [Mnemox — The Complete Guide](table-of-contents.md). Numbers here cite a manifest or say they do not; [`STATUS.md`](../../STATUS.md) is the single home for maturity, coverage and test counts. Chapters 1–9 were written mid-2026 — where a chapter predates a subsystem, chapters 10–12 cover it.

## C.1 Concept Template

**File:** `config/templates/concept.md`

**Purpose:** Document core ideas, definitions, and architectural concepts

**Structure:**

```markdown
---
title: "Concept: [Name]"
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2, tag3]
---

# Concept: [Name]

## Overview
Brief description (2-3 sentences) of what this concept is and why it matters.

## Definition
Detailed explanation of the concept. Include:
- What it is
- Why it exists
- How it fits into the larger system

## Key Components
Main parts or aspects of this concept:
1. Component 1: Description
2. Component 2: Description
3. Component 3: Description

## How It Works
Explain the mechanics or implementation details.

## Examples
Real-world examples demonstrating the concept:

### Example 1: [Name]
Description and code/diagram

### Example 2: [Name]
Description and code/diagram

## Benefits
Why this concept is valuable:
- Benefit 1
- Benefit 2
- Benefit 3

## Trade-offs
Considerations and limitations:
- Trade-off 1
- Trade-off 2

## Related Concepts
- [Related Concept 1](../concepts/related-1.md)
- [Related Concept 2](../concepts/related-2.md)

## References
- External documentation
- Research papers
- Blog posts
```

**When to Use:**
- Explaining architectural patterns
- Defining terminology
- Documenting design decisions
- Clarifying abstract ideas

**Example Topics:**
- Multi-Level Caching
- Token Optimization
- Semantic Similarity
- MECE Framework

## C.2 Guide Template

**File:** `config/templates/guide.md`

**Purpose:** Provide step-by-step instructions for accomplishing tasks

**Structure:**

```markdown
---
title: "Guide: [Task Name]"
type: guide
created: YYYY-MM-DD
updated: YYYY-MM-DD
difficulty: beginner|intermediate|advanced
estimated_time: X minutes
tags: [tag1, tag2, tag3]
---

# Guide: [Task Name]

## Overview
What you'll accomplish by following this guide.

## Prerequisites
What you need before starting:
- Prerequisite 1
- Prerequisite 2
- Prerequisite 3

## Steps

### Step 1: [Action]
Detailed instructions for the first step.

```bash
# Example command
command --option value
```

**Expected output:**
```
Output example
```

### Step 2: [Action]
Detailed instructions for the second step.

### Step 3: [Action]
Continue with remaining steps...

## Verification
How to confirm you've completed the task successfully:

```bash
# Verification command
verify-command
```

**Expected result:**
Description of what success looks like.

## Troubleshooting

### Issue 1: [Problem]
**Symptoms:** What you see when this happens
**Cause:** Why it happens
**Solution:** How to fix it

### Issue 2: [Problem]
Similar format...

## Next Steps
What to do after completing this guide:
- Next action 1
- Next action 2

## Related Guides
- [Related Guide 1](../guides/related-1-guide.md)
- [Related Guide 2](../guides/related-2-guide.md)

## References
- Official documentation
- Tutorial links
```

**When to Use:**
- Installation instructions
- Setup procedures
- How-to tutorials
- Workflow documentation

**Example Topics:**
- Installation Guide
- Quick Start Guide
- Optimization Guide
- Deployment Guide

## C.3 Reference Template

**File:** `config/templates/reference.md`

**Purpose:** Document APIs, specifications, and technical details

**Structure:**

```markdown
---
title: "Reference: [API/Tool Name]"
type: reference
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: X.Y.Z
tags: [tag1, tag2, tag3]
---

# Reference: [API/Tool Name]

## Overview
Brief description of the API/tool and its purpose.

## Installation
```bash
pip install package-name
```

## Import
```python
from module import ClassName
```

## API Reference

### ClassName

**Purpose:** What this class does

**Constructor:**
```python
obj = ClassName(
    param1="value1",
    param2=42
)
```

**Parameters:**
- `param1` (str): Description
- `param2` (int): Description

### Methods

#### method_name(arg1, arg2)

**Purpose:** What this method does

**Parameters:**
- `arg1` (type): Description
- `arg2` (type): Description

**Returns:**
- `return_type`: Description

**Example:**
```python
result = obj.method_name("value", 42)
print(result)
```

**Raises:**
- `ExceptionType`: When this happens

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| option1 | str | "default" | What it does |
| option2 | int | 100 | What it does |

## Examples

### Example 1: Basic Usage
```python
# Code example
```

### Example 2: Advanced Usage
```python
# Code example
```

## Performance Considerations
- Performance tip 1
- Performance tip 2

## Related References
- [Related API 1](../references/related-1-reference.md)
- [Related API 2](../references/related-2-reference.md)

## External Documentation
- Official docs link
- API reference link
```

**When to Use:**
- API documentation
- Configuration options
- Command-line tools
- Technical specifications

**Example Topics:**
- Cache API Reference
- Optimizer Reference
- Script Reference
- Configuration Reference

## C.4 Research Template

**File:** `config/templates/research.md`

**Purpose:** Document investigations, findings, and analysis

**Structure:**

```markdown
---
title: "Research: [Topic] - [Date]"
type: research
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: in-progress|completed
tags: [tag1, tag2, tag3]
---

# Research: [Topic] - [Date]

## Question
What are we investigating?

Clear statement of the research question or problem.

## Hypothesis
What do we expect to find?

State your hypothesis or expected outcome.

## Methodology
How did we investigate?

### Approach
Description of the research approach.

### Tools Used
- Tool 1
- Tool 2
- Tool 3

### Data Collection
How data was collected:
1. Step 1
2. Step 2
3. Step 3

## Findings

### Finding 1: [Title]
**Observation:** What we observed
**Data:** Supporting data or metrics
**Analysis:** What this means

### Finding 2: [Title]
Similar format...

## Data

### Table 1: [Description]
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data     | Data     | Data     |

### Chart 1: [Description]
Description of chart or graph (include image if available)

## Analysis
Detailed analysis of the findings:
- Key insight 1
- Key insight 2
- Key insight 3

## Conclusions
What does this research tell us?

### Main Conclusions
1. Conclusion 1
2. Conclusion 2
3. Conclusion 3

### Implications
What this means for the project:
- Implication 1
- Implication 2

## Limitations
What are the limitations of this research?
- Limitation 1
- Limitation 2

## Next Steps
What should we do next?
1. Action 1
2. Action 2
3. Action 3

## Related Research
- [Related Research 1](../research/related-1-2024-01.md)
- [Related Research 2](../research/related-2-2024-02.md)

## References
- Research paper 1
- Blog post 2
- Documentation 3
```

**When to Use:**
- Performance analysis
- Comparative studies
- Investigation results
- Experimental findings

**Example Topics:**
- Token Savings Analysis
- Cache Performance Study
- Truncation Strategy Comparison
- Scalability Benchmarks

## C.5 Template Variables

### Common Variables

All templates support these variables:

**Metadata:**
- `{title}` - Document title
- `{type}` - Document type (concept, guide, reference, research)
- `{created}` - Creation date (YYYY-MM-DD)
- `{updated}` - Last update date (YYYY-MM-DD)
- `{tags}` - Comma-separated tags

**Content:**
- `{name}` - Primary subject name
- `{description}` - Brief description
- `{author}` - Document author

### Template-Specific Variables

**Guide Template:**
- `{difficulty}` - beginner, intermediate, advanced
- `{estimated_time}` - Time to complete (e.g., "30 minutes")

**Reference Template:**
- `{version}` - API/tool version (e.g., "1.0.0")

**Research Template:**
- `{status}` - in-progress, completed
- `{date}` - Research date (YYYY-MM)

## C.6 Customizing Templates

### Adding Custom Sections

**Example: Adding "Security Considerations" to Guide Template**

```markdown
## Security Considerations
Important security notes:
- Security point 1
- Security point 2
```

### Removing Sections

Simply delete sections you don't need. All sections are optional except:
- Title
- Overview
- Main content area

### Creating Custom Templates

**Steps:**
1. Copy existing template
2. Modify structure
3. Save to `config/templates/`
4. Update Bob Shell configuration
5. Document in this appendix

**Example: Creating "Tutorial" Template**

```markdown
---
title: "Tutorial: {name}"
type: tutorial
created: {created}
updated: {updated}
---

# Tutorial: {name}

## What You'll Learn
- Learning objective 1
- Learning objective 2

## Prerequisites
- Prerequisite 1

## Tutorial Steps
### Part 1: {title}
Content...

## Summary
What you learned.

## Practice Exercises
1. Exercise 1
2. Exercise 2
```

---

**See also:**
- Appendix A: API Reference
- Appendix B: Configuration Reference
- Chapter 5: Knowledge Base Framework
