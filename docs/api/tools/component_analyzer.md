# component_analyzer

Component Analyzer Utility
Analyzes code components with specialized strategies

## Functions

### `main()`

CLI interface for component analyzer


## Classes

### `ComponentAnalyzer`

Analyzes code components with different strategies

#### Methods

##### `__init__(base_path: str)`


##### `analyze_component(component_path: str, analysis_type: AnalysisType, depth: Depth) -> Dict`

Analyze a component (file or directory)

Args:
    component_path: Path to component (file or directory)
    analysis_type: Type of analysis to perform
    depth: Analysis depth (shallow or deep)

Returns:
    Dictionary with analysis results


