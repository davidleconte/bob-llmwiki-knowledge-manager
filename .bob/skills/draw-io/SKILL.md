---
name: draw-io
description: Create draw.io compliant XML diagrams
---
Follow these instructions to create a draw.io compliant XML diagram.

MANDATORY FIRST LINE: Always begin every .drawio file with exactly:
<?xml version="1.0" encoding="UTF-8"?>

GENERATION WORKFLOW (MANDATORY):
Follow this workflow for every diagram generation:
1. Parse Request: Identify diagram type (flowchart, network, architecture, sequence, etc.)
2. Plan Topology: List all vertices with IDs and positions BEFORE generating XML
3. Verify Edges: Ensure all edge source/target IDs exist in your vertex plan
4. Generate XML: Follow progressive template structure (root → vertices → edges)
5. Self-Validate: Check against verification checklist before output

Example Planning Phase:
User Request: "Create flowchart: Start → Process → Decision (Yes/No) → End"
Topology Plan:
- Vertex id="2": Start (rounded rect, x=200, y=80)
- Vertex id="3": Process (rect, x=200, y=180)
- Vertex id="4": Decision (rhombus, x=220, y=280)
- Vertex id="5": End (rounded rect, x=200, y=400)
- Edge id="6": source="2" target="3"
- Edge id="7": source="3" target="4"
- Edge id="8": source="4" target="5" (label="Yes")
Verification: All edge sources/targets (2,3,4,5) exist in vertex list ✓

NON-NEGOTIABLE RULES:
1. ALWAYS start with: <?xml version="1.0" encoding="UTF-8"?>
2. Use infinite canvas: <mxGraphModel dx="1422" dy="762" grid="1" gridSize="10" page="0">
3. Include root structure (files will not open without this):
   <root>
     <mxCell id="0"/>
     <mxCell id="1" parent="0"/>
4. Use sequential IDs starting at 2 (id="0" and id="1" are reserved)
5. Generate ALL vertices BEFORE any edges (prevents orphaned edge references)
6. Every cell needs parent="1" unless grouped
7. Edges must reference valid source and target IDs (both must exist as vertices)
8. Every geometry needs as="geometry" attribute
9. Specify vertex="1" or edge="1" on each cell
10. NEVER quote hex color values: fillColor=#0078D4 not fillColor="#0078D4"
11. Use safe characters in labels - avoid & < > " ' or use word alternatives
12. For multi-line concepts: use hyphens or spaces (e.g., "User Service - Auth"), NEVER literal \n or physical newlines
13. Output ONLY raw XML - no markdown fences, no explanations

ID ALLOCATION STRATEGY:
- Reserve: id="0" (root), id="1" (layer)
- Vertices: id="2" through id="N" (all shapes first)
- Edges: id="N+1" onwards (all connections after)
- Track highest ID used to avoid conflicts
- Never skip numbers in sequence
Example: 3 nodes + 2 edges = vertices (2,3,4) then edges (5,6)

COMMON FAILURE PATTERNS TO AVOID:
❌ Quoted hex colors: style="fillColor="#0078D4" → ✓ style="fillColor=#0078D4"
❌ Missing XML declaration: <mxfile...> → ✓ <?xml version="1.0"...>
❌ Edges before vertices: edge id="3" references id="4" that doesn't exist yet
❌ Literal \n in labels: value="Line1\nLine2" → ✓ value="Line1 - Line2"
❌ Physical newlines in value: value="Line1
   Line2" → ✓ value="Line1 - Line2"

DIAGRAM TYPE TEMPLATES:
- Flowchart: rounded rectangles (start/end), rectangles (process), rhombus (decision)
- Network: ellipse (hub/router), rectangles (devices), labeled edges (connections)
- Architecture: swimlanes (boundaries), cylinders (databases), rectangles (services)
- Sequence: vertical layout, dashed edges (returns), solid edges (calls)

SEMANTIC STYLE PRESETS:
- start_node: rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;
- process_node: rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;
- decision_node: rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;
- end_node: rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;
- database_node: shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#0078D4;strokeColor=#001E4E;fontColor=#ffffff;

LAYOUT BEST PRACTICES:
Proper spacing prevents overlapping elements and improves readability.
- Vertical spacing: 100px minimum between node centers
- Horizontal spacing: 150px minimum between node centers
- Grid alignment: Use multiples of 10 for x,y coordinates (e.g., 100, 150, 200)
- Container padding: 40px minimum from swimlane edges to contained elements
- Standard node dimensions:
  * Rectangle/Process: 120×60
  * Circle/Ellipse: 100×100
  * Rhombus/Decision: 100×80
  * Cylinder/Database: 80×100
  * Swimlane/Container: 200×200 minimum

EDGE LABELS (when needed):
For labeled connections (e.g., "Yes", "No", "HTTP", "1:N"):
<mxCell id="5" value="Yes" edge="1" parent="1" source="2" target="3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>

SHAPE LIBRARY (common styles):
Style syntax: semicolon-separated key=value pairs, no spaces around equals
CRITICAL: Never quote hex color values - fillColor=#0078D4 not fillColor="#0078D4"
- Rectangle: rounded=0;whiteSpace=wrap;html=1;
- Rounded Rectangle: rounded=1;whiteSpace=wrap;html=1;
- Ellipse: ellipse;whiteSpace=wrap;html=1;
- Rhombus (Decision): rhombus;whiteSpace=wrap;html=1;
- Hexagon: shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;
- Parallelogram: shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;
- Cylinder (Database): shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;
- Cloud: ellipse;shape=cloud;whiteSpace=wrap;html=1;
- Swimlane: swimlane;whiteSpace=wrap;html=1;

COLOR PALETTES:
Azure/Professional:
- fillColor=#0078D4;strokeColor=#001E4E;fontColor=#ffffff;
- fillColor=#50E6FF;strokeColor=#0078D4;fontColor=#000000;
Success/Operational:
- fillColor=#107C10;strokeColor=#0E5A0E;fontColor=#ffffff;
- fillColor=#5DB75D;strokeColor=#107C10;fontColor=#000000;
Warning/Error:
- fillColor=#D83B01;strokeColor=#8A2700;fontColor=#ffffff;
- fillColor=#F7630C;strokeColor=#D83B01;fontColor=#000000;
Dark Mode:
- fillColor=#1E1E1E;strokeColor=#3E3E3E;fontColor=#FFFFFF;
- fillColor=#2D2D2D;strokeColor=#555555;fontColor=#FFFFFF;
Light Pastels:
- fillColor=#dae8fc;strokeColor=#6c8ebf;fontColor=#000000;
- fillColor=#d5e8d4;strokeColor=#82b366;fontColor=#000000;
- fillColor=#fff2cc;strokeColor=#d6b656;fontColor=#000000;
- fillColor=#f8cecc;strokeColor=#b85450;fontColor=#000000;

SELF-VERIFICATION CHECKLIST (before XML output):
Verify ALL of these are true before outputting:
✓ First line is exactly: <?xml version="1.0" encoding="UTF-8"?>
✓ <mxGraphModel> has page="0" (infinite canvas)
✓ Root cells id="0" and id="1" parent="0" are present
✓ All cell IDs are unique sequential integers (2, 3, 4...)
✓ All vertices created before any edges
✓ Every edge source and target reference existing vertex IDs
✓ No literal \n (backslash-n) or physical newlines in value attributes
✓ Labels use hyphens/spaces for separation, not newlines
✓ No < or > in labels (use word alternatives)
✓ Hex color values have NO quotes: fillColor=#0078D4 not fillColor="#0078D4"
✓ Every <mxGeometry> has as="geometry" attribute
✓ Every cell has vertex="1" or edge="1" attribute
✓ Every cell has parent="1" (or parent group ID)
✓ No markdown code fences (```xml) wrapping the output
✓ No explanatory text before or after the XML

If ANY checkbox is unchecked, DO NOT output the XML. Fix the issue first.

FINAL REMINDER: When asked to create a .drawio file, output ONLY the raw XML. Do not wrap it in markdown code blocks. Do not add explanations before or after. The output must be valid XML that can be saved directly as a .drawio file.
