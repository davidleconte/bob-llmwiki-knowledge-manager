# batch_file_reader

Batch File Reader Utility
Efficiently reads multiple files with different strategies

## Functions

### `main()`

CLI interface for batch file reader


## Classes

### `BatchFileReader`

Reads multiple files efficiently with different strategies

#### Methods

##### `__init__(base_path: str)`


##### `read_files(file_paths: List[str], strategy: Strategy, search_pattern: Optional[str], max_lines_per_file: int) -> Dict[str, any]`

Read multiple files with specified strategy

Args:
    file_paths: List of file paths to read
    strategy: Reading strategy (full, summary, search)
    search_pattern: Pattern to search for (only for search strategy)
    max_lines_per_file: Maximum lines to read per file

Returns:
    Dictionary with file paths as keys and content/analysis as values


