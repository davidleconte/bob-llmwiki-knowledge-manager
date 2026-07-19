#!/bin/bash

echo "📦 Exporting Knowledge Base..."

KB_DIR="docs/knowledge-base"
OUTPUT_DIR="kb-export"
FORMAT="${1:-markdown}"

if [ ! -d "$KB_DIR" ]; then
    echo "❌ Knowledge base directory not found: $KB_DIR"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

case "$FORMAT" in
    markdown|md)
        echo "📝 Exporting as Markdown (flat structure)..."
        
        # Copy all markdown files to flat structure
        find "$KB_DIR" -name "*.md" -type f | while read -r file; do
            filename=$(basename "$file")
            category=$(basename $(dirname "$file"))
            
            if [ "$category" != "knowledge-base" ]; then
                # Prefix with category
                cp "$file" "$OUTPUT_DIR/${category}-${filename}"
            else
                cp "$file" "$OUTPUT_DIR/${filename}"
            fi
        done
        
        echo "✅ Exported to $OUTPUT_DIR/ (flat markdown)"
        ;;
        
    obsidian)
        echo "📝 Exporting for Obsidian..."
        
        # Copy entire structure
        cp -r "$KB_DIR" "$OUTPUT_DIR/knowledge-base"
        
        # Create Obsidian vault config
        mkdir -p "$OUTPUT_DIR/.obsidian"
        cat > "$OUTPUT_DIR/.obsidian/app.json" << 'OBSIDIAN'
{
  "livePreview": true,
  "readableLineLength": true,
  "strictLineBreaks": false
}
OBSIDIAN
        
        echo "✅ Exported to $OUTPUT_DIR/ (Obsidian vault)"
        echo "   Open $OUTPUT_DIR in Obsidian as a vault"
        ;;

    obsidian-graph)
        echo "📝 Exporting for Obsidian with semantic graph..."

        # Step 1: Obsidian vault copy (same as obsidian case)
        cp -r "$KB_DIR" "$OUTPUT_DIR/knowledge-base"

        mkdir -p "$OUTPUT_DIR/.obsidian"
        cat > "$OUTPUT_DIR/.obsidian/app.json" << 'OBSIDIAN'
{
  "livePreview": true,
  "readableLineLength": true,
  "strictLineBreaks": false
}
OBSIDIAN

        # Step 2: Generate Obsidian Canvas from semantic graph
        python3 scripts/export-kb-graph-canvas.py || exit $?

        # Step 3: Inject Dataview semantic_links frontmatter
        python3 scripts/export-kb-graph-dataview.py || exit $?

        echo "✅ Exported to $OUTPUT_DIR/ (Obsidian vault + semantic graph)"
        echo "   Open $OUTPUT_DIR in Obsidian as a vault"
        echo "   Canvas file  : $OUTPUT_DIR/kb-semantic-graph.canvas"
        echo "   KB documents : $OUTPUT_DIR/knowledge-base/ (annotated with semantic_links)"
        ;;

    html)
        echo "🌐 Exporting as HTML..."
        
        # Check if pandoc is available
        if ! command -v pandoc &> /dev/null; then
            echo "❌ pandoc is required for HTML export"
            echo "   Install: brew install pandoc (macOS) or apt-get install pandoc (Linux)"
            exit 1
        fi
        
        # Convert each markdown file to HTML
        find "$KB_DIR" -name "*.md" -type f | while read -r file; do
            filename=$(basename "$file" .md)
            category=$(basename $(dirname "$file"))
            
            if [ "$category" != "knowledge-base" ]; then
                output_file="$OUTPUT_DIR/${category}-${filename}.html"
            else
                output_file="$OUTPUT_DIR/${filename}.html"
            fi
            
            pandoc "$file" -o "$output_file" --standalone --metadata title="$filename"
        done
        
        echo "✅ Exported to $OUTPUT_DIR/ (HTML files)"
        ;;
        
    pdf)
        echo "📄 Exporting as PDF..."
        
        # Check if pandoc is available
        if ! command -v pandoc &> /dev/null; then
            echo "❌ pandoc is required for PDF export"
            echo "   Install: brew install pandoc (macOS) or apt-get install pandoc (Linux)"
            exit 1
        fi
        
        # Convert each markdown file to PDF
        find "$KB_DIR" -name "*.md" -type f | while read -r file; do
            filename=$(basename "$file" .md)
            category=$(basename $(dirname "$file"))
            
            if [ "$category" != "knowledge-base" ]; then
                output_file="$OUTPUT_DIR/${category}-${filename}.pdf"
            else
                output_file="$OUTPUT_DIR/${filename}.pdf"
            fi
            
            pandoc "$file" -o "$output_file" --pdf-engine=pdflatex 2>/dev/null || \
            pandoc "$file" -o "$output_file" 2>/dev/null || \
            echo "⚠️  Failed to convert $file to PDF"
        done
        
        echo "✅ Exported to $OUTPUT_DIR/ (PDF files)"
        ;;
        
    *)
        echo "❌ Unknown format: $FORMAT"
        echo ""
        echo "Usage: $0 [format]"
        echo ""
        echo "Available formats:"
        echo "  markdown, md    - Flat markdown structure (default)"
        echo "  obsidian        - Obsidian vault format"
        echo "  obsidian-graph  - Obsidian vault + Canvas semantic graph + Dataview annotations"
        echo "  html            - HTML files (requires pandoc)"
        echo "  pdf             - PDF files (requires pandoc)"
        echo ""
        echo "Examples:"
        echo "  $0              # Export as markdown"
        echo "  $0 obsidian     # Export for Obsidian"
        echo "  $0 obsidian-graph  # Export for Obsidian with semantic graph"
        echo "  $0 html         # Export as HTML"
        exit 1
        ;;
esac

echo ""
echo "📊 Export Statistics:"
echo "  Total files: $(find "$OUTPUT_DIR" -type f | wc -l)"
echo "  Output directory: $OUTPUT_DIR"
