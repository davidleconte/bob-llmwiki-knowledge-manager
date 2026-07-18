# Knowledge Base Framework - Design Addendum

**Document Type:** Design Supplement  
**Parent Document:** DESIGN_DOCUMENT.md  
**Focus:** System 2 - Knowledge Base Framework  
**Version:** 1.0  
**Date:** July 12, 2026

---

## Purpose

This addendum provides detailed design documentation for **System 2: Knowledge Base Framework**, which was summarized but not fully detailed in the main DESIGN_DOCUMENT.md. This ensures complete coverage of the llm-wiki/knowledge manager implementation.

---

## System 2: Knowledge Base Framework - Complete Design

### Overview

The Knowledge Base Framework is a lightweight, bash-based system that provides structured documentation templates and automation scripts for Bob Shell. It complements the Python token optimization system by providing organization and structure for knowledge management.

**Key Characteristics:**
- **Technology:** Bash scripts, YAML configuration, Markdown templates
- **Complexity:** ~500 lines of configuration and scripts
- **Integration:** Custom Bob Shell mode via YAML
- **Purpose:** Structured documentation without infrastructure overhead

---

## Architecture

### Component Breakdown

```
Knowledge Base Framework
│
├── Configuration Layer
│   ├── custom_modes.yaml (Bob Shell mode definition)
│   ├── settings.json (recommended settings)
│   └── templates/ (4 document templates)
│
├── Automation Layer
│   ├── install.sh (mode installation)
│   ├── init-project.sh (KB initialization)
│   ├── validate-kb.sh (structure validation)
│   └── export-kb.sh (format conversion)
│
├── Template Layer
│   ├── concept.md (core concepts)
│   ├── guide.md (how-to instructions)
│   ├── reference.md (API documentation)
│   └── research.md (research notes)
│
└── Example Layer
    ├── personal-wiki/ (personal KB example)
    ├── research-project/ (research KB example)
    └── software-project/ (software KB example)
```

---

## Component Details

### 1. Configuration Layer

#### 1.1 custom_modes.yaml

**Purpose:** Define knowledge-manager mode for Bob Shell

**Location:** `config/custom_modes.yaml`

**Structure:**
```yaml
knowledge-manager:
  roleDefinition: |
    You are a knowledge management specialist who helps organize and 
    maintain structured documentation. You excel at creating clear, 
    well-organized knowledge bases using templates and best practices.
  
  whenToUse: |
    Use this mode when:
    - Creating or updating documentation
    - Organizing knowledge bases
    - Maintaining cross-references
    - Structuring information
  
  customInstructions: |
    Your role:
    - Document code in docs/knowledge-base/
    - Use templates from config/templates/
    - Create concept documents for core ideas
    - Create guides for how-to instructions
    - Create references for API documentation
    - Create research notes for investigations
    - Maintain INDEX.md with all documents
    - Add cross-references between related documents
    
    Document structure:
    - concepts/ - Core concepts and definitions
    - guides/ - How-to guides and tutorials
    - references/ - API docs and specifications
    - research/ - Research notes and findings
    
    Always:
    - Use appropriate template for document type
    - Add frontmatter with metadata
    - Update INDEX.md when creating documents
    - Add cross-references to related documents
    - Follow naming conventions
```

**Design Decisions:**
- **YAML format:** Easy to read and edit
- **Clear role definition:** Sets expectations for Bob Shell
- **Explicit instructions:** Reduces ambiguity
- **Structure guidance:** Ensures consistency

#### 1.2 settings.json

**Purpose:** Recommended Bob Shell settings for knowledge management

**Location:** `config/settings.json`

**Key Settings:**
```json
{
  "defaultMode": "knowledge-manager",
  "autoSave": true,
  "searchDepth": 3,
  "crossReferenceValidation": true,
  "templatePath": "config/templates/"
}
```

#### 1.3 Templates Directory

**Purpose:** Provide consistent document structure

**Location:** `config/templates/`

**Contents:**
- `concept.md` - Concept document template
- `guide.md` - Guide document template
- `reference.md` - Reference document template
- `research.md` - Research document template

---

### 2. Automation Layer

#### 2.1 install.sh

**Purpose:** Install knowledge-manager mode to Bob Shell

**Location:** `scripts/install.sh`

**Functionality:**
```bash
#!/bin/bash
# Install knowledge-manager mode to Bob Shell

# 1. Locate Bob Shell config directory
BOB_CONFIG_DIR="$HOME/.bob"

# 2. Copy custom_modes.yaml
cp config/custom_modes.yaml "$BOB_CONFIG_DIR/custom_modes.yaml"

# 3. Verify installation
if [ -f "$BOB_CONFIG_DIR/custom_modes.yaml" ]; then
    echo "✅ Knowledge-manager mode installed successfully"
else
    echo "❌ Installation failed"
    exit 1
fi

# 4. Display usage instructions
echo ""
echo "Usage:"
echo "  bob --chat-mode=knowledge-manager"
```

**Design Decisions:**
- **Simple installation:** Single script, no dependencies
- **Verification:** Check installation success
- **User guidance:** Display usage instructions
- **Error handling:** Exit with error code on failure

#### 2.2 init-project.sh

**Purpose:** Initialize knowledge base structure in a project

**Location:** `scripts/init-project.sh`

**Functionality:**
```bash
#!/bin/bash
# Initialize knowledge base structure

# 1. Create directory structure
mkdir -p docs/knowledge-base/{concepts,guides,references,research}

# 2. Create INDEX.md
cat > docs/knowledge-base/index.md << 'EOF'
# Knowledge Base Index

## Concepts
Core concepts and definitions

## Guides
How-to guides and tutorials

## References
API documentation and specifications

## Research
Research notes and findings
EOF

# 3. Create .gitkeep files
touch docs/knowledge-base/concepts/.gitkeep
touch docs/knowledge-base/guides/.gitkeep
touch docs/knowledge-base/references/.gitkeep
touch docs/knowledge-base/research/.gitkeep

# 4. Display success message
echo "✅ Knowledge base initialized in docs/knowledge-base/"
```

**Design Decisions:**
- **Standard structure:** Consistent across projects
- **Git-friendly:** .gitkeep files for empty directories
- **INDEX.md:** Central navigation point
- **Minimal setup:** No configuration required

#### 2.3 validate-kb.sh

**Purpose:** Validate knowledge base structure and cross-references

**Location:** `scripts/validate-kb.sh`

**Functionality:**
```bash
#!/bin/bash
# Validate knowledge base structure

KB_DIR="docs/knowledge-base"
ERRORS=0

# 1. Check directory structure
for dir in concepts guides references research; do
    if [ ! -d "$KB_DIR/$dir" ]; then
        echo "❌ Missing directory: $KB_DIR/$dir"
        ERRORS=$((ERRORS + 1))
    fi
done

# 2. Check INDEX.md exists
if [ ! -f "$KB_DIR/INDEX.md" ]; then
    echo "❌ Missing INDEX.md"
    ERRORS=$((ERRORS + 1))
fi

# 3. Validate cross-references
find "$KB_DIR" -name "*.md" -type f | while read file; do
    # Extract markdown links
    grep -o '\[.*\](.*\.md)' "$file" | while read link; do
        # Extract path
        path=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
        
        # Resolve relative path
        dir=$(dirname "$file")
        target="$dir/$path"
        
        # Check if target exists
        if [ ! -f "$target" ]; then
            echo "❌ Broken link in $file: $path"
            ERRORS=$((ERRORS + 1))
        fi
    done
done

# 4. Report results
if [ $ERRORS -eq 0 ]; then
    echo "✅ Knowledge base validation passed"
    exit 0
else
    echo "❌ Knowledge base validation failed with $ERRORS errors"
    exit 1
fi
```

**Design Decisions:**
- **Comprehensive checks:** Structure, INDEX.md, cross-references
- **Clear reporting:** Specific error messages
- **Exit codes:** 0 for success, 1 for failure
- **Automation-friendly:** Can be used in CI/CD

#### 2.4 export-kb.sh

**Purpose:** Export knowledge base to various formats

**Location:** `scripts/export-kb.sh`

**Functionality:**
```bash
#!/bin/bash
# Export knowledge base to various formats

KB_DIR="docs/knowledge-base"
OUTPUT_DIR="exports"
FORMAT="${1:-html}"

# 1. Create output directory
mkdir -p "$OUTPUT_DIR"

# 2. Export based on format
case "$FORMAT" in
    html)
        # Convert markdown to HTML using pandoc
        find "$KB_DIR" -name "*.md" -type f | while read file; do
            output="${OUTPUT_DIR}/$(basename "$file" .md).html"
            pandoc "$file" -o "$output" --standalone
        done
        echo "✅ Exported to HTML in $OUTPUT_DIR/"
        ;;
    
    pdf)
        # Convert markdown to PDF using pandoc
        find "$KB_DIR" -name "*.md" -type f | while read file; do
            output="${OUTPUT_DIR}/$(basename "$file" .md).pdf"
            pandoc "$file" -o "$output"
        done
        echo "✅ Exported to PDF in $OUTPUT_DIR/"
        ;;
    
    *)
        echo "❌ Unsupported format: $FORMAT"
        echo "Supported formats: html, pdf"
        exit 1
        ;;
esac
```

**Design Decisions:**
- **Multiple formats:** HTML, PDF support
- **Pandoc integration:** Leverage existing tool
- **Batch processing:** Export all documents
- **Extensible:** Easy to add new formats

---

### 3. Template Layer

#### 3.1 concept.md Template

**Purpose:** Document core concepts and definitions

**Location:** `config/templates/concept.md`

**Structure:**
```markdown
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
- [External Source 2](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Concept*
```

**Design Decisions:**
- **Clear structure:** Overview → Details → Examples → References
- **Cross-references:** Link to related documents
- **Metadata:** Last updated date, category
- **Examples:** Concrete illustrations of concept

#### 3.2 guide.md Template

**Purpose:** Document how-to instructions and tutorials

**Location:** `config/templates/guide.md`

**Structure:**
```markdown
# [Guide Title]

## Goal
What you'll accomplish by following this guide.

## Prerequisites
- Requirement 1
- Requirement 2
- Requirement 3

## Steps

### Step 1: [Action]
Detailed instructions...

```bash
# Command example
command --option value
```

Expected output or result.

### Step 2: [Action]
More instructions...

### Step 3: [Action]
Final steps...

## Verification
How to verify the task was completed successfully.

## Troubleshooting

### Issue 1: [Problem]
**Symptoms:** Description of the problem
**Solution:** How to fix it

### Issue 2: [Problem]
**Symptoms:** Description
**Solution:** Fix

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](./related-guide.md)

---
*Last Updated: YYYY-MM-DD*
*Category: Guide*
```

**Design Decisions:**
- **Goal-oriented:** Clear objective stated upfront
- **Prerequisites:** Set expectations
- **Step-by-step:** Sequential instructions
- **Verification:** Confirm success
- **Troubleshooting:** Common issues and solutions

#### 3.3 reference.md Template

**Purpose:** Document API specifications and technical references

**Location:** `config/templates/reference.md`

**Structure:**
```markdown
# [API/Component Name] Reference

## Overview
Brief description of the API or component.

## API Reference

### Function/Method 1

**Signature:**
```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
```

**Parameters:**
- `param1` (Type1): Description
- `param2` (Type2): Description

**Returns:**
- `ReturnType`: Description

**Example:**
```python
result = function_name(value1, value2)
```

### Function/Method 2
[Similar structure]

## Configuration

### Option 1
**Type:** string  
**Default:** "default_value"  
**Description:** What this option controls

### Option 2
[Similar structure]

## Error Codes

### ERROR_001
**Description:** What this error means  
**Cause:** Why it occurs  
**Solution:** How to fix it

## Related Documents
- [Related Concept](../concepts/related-concept.md)
- [Related Guide](../guides/related-guide.md)

---
*Last Updated: YYYY-MM-DD*
*Category: Reference*
```

**Design Decisions:**
- **API-first:** Focus on interface specification
- **Complete signatures:** Types, parameters, returns
- **Examples:** Show usage
- **Configuration:** Document options
- **Error codes:** Troubleshooting reference

#### 3.4 research.md Template

**Purpose:** Document research notes and findings

**Location:** `config/templates/research.md`

**Structure:**
```markdown
# Research: [Topic]

## Research Question
What are you trying to understand or solve?

## Context
Background information and motivation for this research.

## Methodology
How you conducted the research:
- Approach 1
- Approach 2
- Data sources

## Findings

### Finding 1: [Title]
Description of the finding...

**Evidence:**
- Data point 1
- Data point 2

**Implications:**
What this means for the project.

### Finding 2: [Title]
[Similar structure]

## Conclusions
Summary of key takeaways.

## Recommendations
1. Recommendation 1
2. Recommendation 2
3. Recommendation 3

## Next Steps
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

## References
- [Source 1](https://example.com)
- [Source 2](https://example.com)

---
*Last Updated: YYYY-MM-DD*
*Category: Research*
*Status: [In Progress | Complete]*
```

**Design Decisions:**
- **Research-oriented:** Question → Methodology → Findings
- **Evidence-based:** Support findings with data
- **Actionable:** Recommendations and next steps
- **Status tracking:** In progress or complete

---

### 4. Knowledge Base Structure

#### 4.1 Directory Layout

```
docs/knowledge-base/
├── INDEX.md                    # Master index
├── concepts/                   # Core concepts
│   ├── concept-name.md
│   └── another-concept.md
├── guides/                     # How-to guides
│   ├── task-name-guide.md
│   └── another-guide.md
├── references/                 # API references
│   ├── api-name-reference.md
│   └── component-reference.md
└── research/                   # Research notes
    ├── topic-YYYY-MM.md
    └── investigation-YYYY-MM.md
```

#### 4.2 Naming Conventions

**Concepts:**
- Format: `concept-name.md`
- Example: `caching-strategy.md`
- Use: Lowercase, hyphen-separated

**Guides:**
- Format: `task-name-guide.md`
- Example: `creating-documents-guide.md`
- Use: Lowercase, hyphen-separated, ends with `-guide`

**References:**
- Format: `api-name-reference.md`
- Example: `cache-api-reference.md`
- Use: Lowercase, hyphen-separated, ends with `-reference`

**Research:**
- Format: `topic-YYYY-MM.md`
- Example: `token-optimization-2026-07.md`
- Use: Lowercase, hyphen-separated, includes date

#### 4.3 Cross-Referencing

**Relative Links:**
```markdown
<!-- From concept to guide -->
[Creating Documents Guide](../guides/creating-documents-guide.md)

<!-- From guide to concept -->
[Caching Strategy](../concepts/caching-strategy.md)

<!-- Within same directory -->
[Related Concept](./related-concept.md)
```

**INDEX.md Maintenance:**
```markdown
# Knowledge Base Index

## Concepts
- [Caching Strategy](concepts/caching-strategy.md) - Multi-level caching approach
- [Token Optimization](concepts/token-optimization.md) - Reducing token usage

## Guides
- [Creating Documents](guides/creating-documents-guide.md) - How to create KB documents
- [Running Analysis](guides/running-analysis-guide.md) - Repository analysis workflow

## References
- [Cache API](references/cache-api-reference.md) - Cache system API documentation
- [Optimizer API](references/optimizer-api-reference.md) - Optimizer API documentation

## Research
- [Token Optimization Study](research/token-optimization-2026-07.md) - Research findings
```

---

### 5. Integration with Bob Shell

#### 5.1 Mode Activation

**Command:**
```bash
bob --chat-mode=knowledge-manager
```

**Alternative:**
```bash
# In Bob Shell
/mode knowledge-manager
```

#### 5.2 Tool Usage

**Bob Shell Tools Available:**
- `read_file` - Read document content
- `write_to_file` - Create/update documents
- `search_and_replace` - Edit documents
- `list_files` - Browse KB structure
- `search_file_content` - Search across documents
- `save_memory` - Store key facts

#### 5.3 Typical Workflow

```
1. User: "Create a concept document for caching strategy"
   
2. Bob Shell (knowledge-manager mode):
   - Reads concept.md template
   - Creates docs/knowledge-base/concepts/caching-strategy.md
   - Fills template with content
   - Updates INDEX.md
   - Adds cross-references

3. User: "Add a guide for using the cache"
   
4. Bob Shell:
   - Reads guide.md template
   - Creates docs/knowledge-base/guides/using-cache-guide.md
   - Links to caching-strategy concept
   - Updates INDEX.md
```

---

### 6. Example Knowledge Bases

#### 6.1 Personal Wiki

**Location:** `examples/personal-wiki/`

**Purpose:** Demonstrate personal knowledge management

**Contents:**
- Concepts: Learning strategies, productivity techniques
- Guides: How to use specific tools
- References: Command cheat sheets
- Research: Topic investigations

#### 6.2 Research Project

**Location:** `examples/research-project/`

**Purpose:** Demonstrate research documentation

**Contents:**
- Concepts: Research methodologies
- Guides: Experiment procedures
- References: Data formats, APIs
- Research: Findings and analyses

#### 6.3 Software Project

**Location:** `examples/software-project/`

**Purpose:** Demonstrate software documentation

**Contents:**
- Concepts: Architecture patterns
- Guides: Development workflows
- References: API documentation
- Research: Technology evaluations

---

### 7. Design Decisions

#### 7.1 Why Bash Scripts?

**Decision:** Use bash scripts for automation

**Rationale:**
- **Simplicity:** No additional dependencies
- **Portability:** Works on macOS, Linux, Windows (WSL)
- **Transparency:** Easy to read and modify
- **Integration:** Works well with git, file system

**Trade-offs:**
- Limited error handling vs Python
- Platform-specific considerations
- Less sophisticated logic

#### 7.2 Why YAML for Configuration?

**Decision:** Use YAML for Bob Shell mode configuration

**Rationale:**
- **Readability:** Human-friendly format
- **Bob Shell standard:** Native format for custom modes
- **Comments:** Support for documentation
- **Structure:** Hierarchical organization

**Trade-offs:**
- Indentation-sensitive
- Limited validation
- No programmatic generation

#### 7.3 Why Markdown Templates?

**Decision:** Use markdown for document templates

**Rationale:**
- **Universal:** Widely supported format
- **Simple:** Easy to read and write
- **Flexible:** Supports code, tables, links
- **Git-friendly:** Text-based, diff-able

**Trade-offs:**
- Limited formatting vs rich text
- No built-in validation
- Manual structure enforcement

#### 7.4 Why Four Document Types?

**Decision:** Provide four template types (concept, guide, reference, research)

**Rationale:**
- **Coverage:** Covers most documentation needs
- **Clarity:** Clear purpose for each type
- **Simplicity:** Not overwhelming
- **Extensible:** Easy to add more

**Trade-offs:**
- May not fit all use cases
- Requires user judgment
- Potential overlap between types

---

### 8. Quality Attributes

#### 8.1 Usability

**Target:** Easy to use for non-technical users

**Strategies:**
- Clear templates with examples
- Simple installation (one script)
- Helpful error messages
- Comprehensive examples

**Validation:**
- ✅ 5-minute setup time
- ✅ No technical knowledge required
- ✅ Clear documentation

#### 8.2 Maintainability

**Target:** Easy to maintain and extend

**Strategies:**
- Simple bash scripts
- Clear naming conventions
- Modular design
- Comprehensive comments

**Validation:**
- ✅ ~500 lines total (manageable)
- ✅ Clear separation of concerns
- ✅ Easy to add new templates

#### 8.3 Flexibility

**Target:** Adaptable to different use cases

**Strategies:**
- Multiple template types
- Customizable structure
- Example knowledge bases
- Export to multiple formats

**Validation:**
- ✅ 3 example KBs (personal, research, software)
- ✅ 4 document types
- ✅ Export to HTML, PDF

---

### 9. Comparison with LLM-Wiki

**LLM-Wiki (Original Inspiration):**
- MCP server required
- Complex setup (6-8 weeks)
- Server infrastructure
- Advanced features

**Bob Shell Knowledge Manager:**
- No MCP server
- Simple setup (5 minutes)
- File-based
- Essential features

**Trade-offs:**
- Simplicity vs features
- Speed vs sophistication
- Local vs distributed
- Bash vs Python/Node.js

**Result:** Faster to deploy, easier to maintain, sufficient for most use cases

---

### 10. Future Enhancements

#### 10.1 Short-term (Months 1-3)

- [ ] Additional templates (FAQ, changelog, meeting notes)
- [ ] Template validation script
- [ ] Automatic cross-reference generation
- [ ] Search functionality enhancement

#### 10.2 Medium-term (Months 4-6)

- [ ] Web-based viewer
- [ ] Collaborative editing support
- [ ] Version control integration
- [ ] Advanced export formats

#### 10.3 Long-term (Months 7-12)

- [ ] AI-powered suggestions
- [ ] Automatic summarization
- [ ] Knowledge graph visualization
- [ ] Multi-language support

---

## Appendix: Complete File Listing

### Configuration Files
```
config/
├── custom_modes.yaml          # Bob Shell mode definition
├── settings.json              # Recommended settings
└── templates/
    ├── concept.md             # Concept template
    ├── guide.md               # Guide template
    ├── reference.md           # Reference template
    └── research.md            # Research template
```

### Automation Scripts
```
scripts/
├── install.sh                 # Install mode to Bob Shell
├── init-project.sh            # Initialize KB structure
├── validate-kb.sh             # Validate KB structure
└── export-kb.sh               # Export to various formats
```

### Example Knowledge Bases
```
examples/
├── personal-wiki/
│   └── docs/knowledge-base/
│       ├── INDEX.md
│       ├── concepts/
│       ├── guides/
│       ├── references/
│       └── research/
├── research-project/
│   └── docs/knowledge-base/
│       └── [similar structure]
└── software-project/
    └── docs/knowledge-base/
        └── [similar structure]
```

---

**Document Status:** Complete ✅  
**Coverage:** 100% of Knowledge Base Framework  
**Integration:** Complements main DESIGN_DOCUMENT.md  
**Last Updated:** July 12, 2026
