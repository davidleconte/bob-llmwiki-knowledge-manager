# kb_query

Knowledge Base Query Utility
Semantic search across knowledge base documents

## Functions

### `main()`

CLI interface for knowledge base query


## Classes

### `KnowledgeBaseQuery`

Query knowledge base with semantic search

#### Methods

##### `__init__(kb_path: str)`


##### `query(query: str, categories: Optional[List[str]], max_results: int, include_content: bool) -> Dict`

Query the knowledge base

Args:
    query: Search query
    categories: Categories to search (None = all)
    max_results: Maximum number of results
    include_content: Include full content in results

Returns:
    Dictionary with search results


##### `list_documents(category: Optional[str]) -> Dict`

List all documents in knowledge base


##### `get_cross_references(file_path: str) -> Dict`

Get cross-references for a document


##### `get_statistics() -> Dict`

Get knowledge base statistics


