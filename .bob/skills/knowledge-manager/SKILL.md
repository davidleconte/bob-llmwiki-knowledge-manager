---
name: knowledge-manager
description: >
  Full workflow instructions for the Knowledge Manager mode -- document templates,
  naming conventions, cross-reference protocol, and INDEX.md maintenance.
  Use when creating or updating knowledge base content in Bob IDE.
triggers:
  - "create a concept document"
  - "create a guide"
  - "create a reference document"
  - "write a research note"
  - "update the knowledge base"
  - "update INDEX.md"
  - "add to the knowledge base"
  - "document this in the KB"
  - "knowledge base template"
---

# Knowledge Manager Skill

This skill provides the full template corpus and workflow protocol for the
`knowledge-manager` Bob IDE mode. Activate it when creating or updating any
knowledge base document.

---

## Document Templates

### Concept (`docs/knowledge-base/concepts/concept-name.md`)

````markdown
# [Concept Name]

## Overview
Brief description of the concept (2-3 sentences).

## Key Points
- Main idea 1
- Main idea 2
- Main idea 3

## Details

### Subsection 1
Detailed explanation...

### Subsection 2
More details...

## Examples

### Example 1: [Scenario]
```
Code or command example
```

Explanation of the example.

## Related Documents
- [Related Concept 1](./related-concept-1.md)
- [Related Guide](../guides/related-guide.md)

## References
- [External Source 1](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Concept*
````

---

### Guide (`docs/knowledge-base/guides/task-name-guide.md`)

````markdown
# [Task Name] Guide

## Overview
Brief description of what this guide covers and who it's for.

## Prerequisites
- Prerequisite 1
- Prerequisite 2

## Steps

### Step 1: [Action]
Detailed instructions.

```bash
# Example command
command --option value
```

### Step 2: [Action]
Detailed instructions.

## Verification
How to verify the task completed successfully:

```bash
verify-command
```

Expected output:
```
Expected result
```

## Troubleshooting

### Issue 1: [Problem Description]
**Symptoms**: What you see.
**Cause**: Why this happens.
**Solution**: How to fix it.

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](./related-guide.md)

## References
- [Official Documentation](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Guide*
````

---

### Reference (`docs/knowledge-base/references/api-name-reference.md`)

````markdown
# [API/Component Name] Reference

## Overview
Brief description of what this reference covers.

## API Endpoints / Components

### Endpoint/Component 1
**Description**: What it does.

**Parameters**:
- `param1` (type): Description

**Returns**: Description of return value.

**Example**:
```
Example usage
```

## Common Patterns

### Pattern 1: [Use Case]
```
Example code
```

## Error Handling

### Error 1: [Error Code/Name]
**Cause**: Why this error occurs.
**Solution**: How to handle it.

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](../guides/related-guide.md)

---
*Last Updated: YYYY-MM-DD*
*Category: Reference*
````

---

### Research (`docs/knowledge-base/research/topic-YYYY-MM.md`)

````markdown
# [Topic] Research - [Month YYYY]

## Objective
What we're researching and why.

## Background
Context and motivation.

## Findings

### Finding 1: [Title]
Description.

**Evidence**:
- Data point 1

## Analysis

### Interpretation
What the findings mean.

### Implications
How this affects our work.

## Conclusions

### Recommendations
1. Recommendation 1

### Next Steps
- Action item 1

## Sources
- [Source 1](https://example.com)

## Related Documents
- [Related Concept](../concepts/related-concept.md)

---
*Last Updated: YYYY-MM-DD*
*Category: Research*
````

---

## Cross-Reference Protocol

Every document must link **bidirectionally**:

1. When you add a link from document A to document B, open document B and add the
   reciprocal link back to A under its **Related Documents** section.
2. Use relative paths from the document's own directory:
   - `../concepts/name.md` from guides/
   - `../guides/name.md` from concepts/
   - `./sibling.md` within the same folder

---

## INDEX.md Maintenance

After creating or updating any document, add or refresh its entry in
`docs/knowledge-base/INDEX.md` under the correct category heading:

````markdown
## Concepts
- [Concept Name](concepts/concept-name.md) - One-line description

## Guides
- [Task Name Guide](guides/task-name-guide.md) - One-line description

## References
- [API Name Reference](references/api-name-reference.md) - One-line description

## Research
- [Topic YYYY-MM](research/topic-YYYY-MM.md) - One-line description
````

---

## Naming Conventions (quick reference)

| Category  | File name pattern          | Example                     |
|-----------|----------------------------|-----------------------------|
| Concept   | `concept-name.md`          | `token-caching.md`          |
| Guide     | `task-name-guide.md`       | `setup-kb-guide.md`         |
| Reference | `api-name-reference.md`    | `cache-api-reference.md`    |
| Research  | `topic-YYYY-MM.md`         | `delegation-2026-07.md`     |

---

## Persistence note (Bob IDE)

Bob IDE has no `save_memory` tool. All knowledge persistence is achieved by
writing markdown files to `docs/knowledge-base/`. Commit those files to git so they
survive across sessions and team members can benefit from them.
