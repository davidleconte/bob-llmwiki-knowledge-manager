#!/bin/bash

echo "🔍 Validating Knowledge Base..."

KB_DIR="docs/knowledge-base"

if [ ! -d "$KB_DIR" ]; then
    echo "❌ Knowledge base directory not found: $KB_DIR"
    exit 1
fi

# Check for index.md
if [ ! -f "$KB_DIR/index.md" ]; then
    echo "❌ index.md not found"
    exit 1
fi
echo "✅ index.md exists"

# Check for required directories
for dir in concepts guides references research; do
    if [ ! -d "$KB_DIR/$dir" ]; then
        echo "❌ Missing directory: $dir"
        exit 1
    fi
    echo "✅ Directory exists: $dir"
done

# Check for broken links
echo ""
echo "🔗 Checking for broken links..."
broken_links=0

find "$KB_DIR" -name "*.md" -type f | while read -r file; do
    grep -oP '\[.*?\]\(\K[^)]+' "$file" 2>/dev/null | while read -r link; do
        if [[ $link =~ ^https?:// ]]; then
            continue
        fi
        
        dir=$(dirname "$file")
        target="$dir/$link"
        
        if [ ! -f "$target" ]; then
            echo "❌ Broken link in $file: $link"
            broken_links=$((broken_links + 1))
        fi
    done
done

if [ $broken_links -eq 0 ]; then
    echo "✅ No broken links found"
fi

echo ""
echo "📊 Knowledge Base Statistics:"
echo "  Concepts: $(find "$KB_DIR/concepts" -name "*.md" -type f 2>/dev/null | wc -l)"
echo "  Guides: $(find "$KB_DIR/guides" -name "*.md" -type f 2>/dev/null | wc -l)"
echo "  References: $(find "$KB_DIR/references" -name "*.md" -type f 2>/dev/null | wc -l)"
echo "  Research: $(find "$KB_DIR/research" -name "*.md" -type f 2>/dev/null | wc -l)"
echo "  Total: $(find "$KB_DIR" -name "*.md" -type f 2>/dev/null | wc -l)"

# ── Root-file hygiene check ───────────────────────────────────────────────────
echo ""
echo "🏠 Checking root-file hygiene..."
# Allowed root-level .md files (conventional artefacts only)
ALLOWED_ROOT_MD="README.md AGENTS.md STATUS.md CHANGELOG.md INTEGRATIONS.md CODE_OF_CONDUCT.md CONTRIBUTING.md GOVERNANCE.md SECURITY.md SUPPORT.md"
root_hygiene_ok=1
for f in *.md; do
    [[ -f "$f" ]] || continue          # glob matched nothing
    allowed=0
    for a in $ALLOWED_ROOT_MD; do
        [[ "$f" == "$a" ]] && { allowed=1; break; }
    done
    if [[ $allowed -eq 0 ]]; then
        echo "⚠️  Stray root-level .md: $f  (move to docs/project-management/plans/ or docs/)"
        root_hygiene_ok=0
    fi
done
if [[ $root_hygiene_ok -eq 1 ]]; then
    echo "✅ Root-file hygiene OK (no stray .md files)"
fi
