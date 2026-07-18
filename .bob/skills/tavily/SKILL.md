# Tavily REMO MCP Server - Internet Search Skill

## Overview
The Tavily REMO MCP server provides real-time internet search capabilities, allowing Bob to search the web for current information, news, facts, and data beyond the knowledge cutoff date.

## When to Use Tavily Search

### Trigger Phrases
Bob should automatically use Tavily search when the user requests:
- "search on internet..."
- "search on the net..."
- "search the web..."
- "look up online..."
- "find information about..."
- "what's the latest on..."
- "search for..."
- "google..."
- "find current information..."
- "what's happening with..."
- "latest news about..."

### Use Cases
1. **Current Events & News**: When users ask about recent events, news, or developments
2. **Real-time Information**: Stock prices, weather, sports scores, current statistics
3. **Fact Checking**: Verifying current information or recent changes
4. **Research**: Finding documentation, articles, or resources on specific topics
5. **Technology Updates**: Latest versions, releases, or announcements
6. **Beyond Knowledge Cutoff**: Any information that may have changed or emerged after Bob's training data

## Available Tools

### tavily_search
Search the web for current information on any topic.

**Parameters:**
- `query` (required): Search query string
- `max_results` (optional): Maximum number of results to return (default: 5)
- `search_depth` (optional): Search depth - "basic", "advanced", "fast", or "ultra-fast" (default: "basic")
- `topic` (optional): Category of search - "general" (default)
- `time_range` (optional): Time range - "day", "week", "month", "year", or null
- `include_images` (optional): Include query-related images (default: false)
- `include_image_descriptions` (optional): Include images with descriptions (default: false)
- `include_raw_content` (optional): Include cleaned HTML content (default: false)
- `include_domains` (optional): Array of domains to specifically include
- `exclude_domains` (optional): Array of domains to specifically exclude
- `country` (optional): Boost results from specific country (full name, e.g., "United States")
- `include_favicon` (optional): Include favicon URLs (default: false)
- `start_date` (optional): Return results after this date (YYYY-MM-DD format)
- `end_date` (optional): Return results before this date (YYYY-MM-DD format)
- `exact_match` (optional): Only return results with exact phrase matches

**Usage Example:**
```xml
<use_mcp_tool>
<server_name>tavily-remo</server_name>
<tool_name>tavily_search</tool_name>
<arguments>
{
  "query": "latest IBM watsonx updates 2024",
  "max_results": 10,
  "search_depth": "advanced",
  "time_range": "month"
}
</arguments>
</use_mcp_tool>
```

### tavily_extract
Extract content from specific URLs.

**Parameters:**
- `urls` (required): Array of URLs to extract content from
- `extract_depth` (optional): "basic" or "advanced" (use advanced for LinkedIn, protected sites, tables)
- `include_images` (optional): Include images from pages (default: false)
- `format` (optional): Output format - "markdown" or "text" (default: "markdown")
- `include_favicon` (optional): Include favicon URLs (default: false)
- `query` (optional): Query to rerank content chunks by relevance

**Usage Example:**
```xml
<use_mcp_tool>
<server_name>tavily-remo</server_name>
<tool_name>tavily_extract</tool_name>
<arguments>
{
  "urls": ["https://www.ibm.com/products/watsonx-ai"],
  "extract_depth": "advanced",
  "format": "markdown"
}
</arguments>
</use_mcp_tool>
```

### tavily_crawl
Crawl a website starting from a URL to extract content from multiple pages.

**Parameters:**
- `url` (required): Root URL to begin crawling
- `max_depth` (optional): Maximum crawl depth (default: 1, minimum: 1)
- `max_breadth` (optional): Maximum links per page level (default: 20, minimum: 1)
- `limit` (optional): Total links to process (default: 50, minimum: 1)
- `instructions` (optional): Natural language instructions for crawler
- `select_paths` (optional): Regex patterns for URL path filtering
- `select_domains` (optional): Regex patterns for domain filtering
- `allow_external` (optional): Return external links (default: true)
- `extract_depth` (optional): "basic" or "advanced"
- `format` (optional): "markdown" or "text" (default: "markdown")
- `include_favicon` (optional): Include favicon URLs (default: false)

**Usage Example:**
```xml
<use_mcp_tool>
<server_name>tavily-remo</server_name>
<tool_name>tavily_crawl</tool_name>
<arguments>
{
  "url": "https://www.ibm.com/docs/en/watsonx",
  "max_depth": 2,
  "max_breadth": 10,
  "instructions": "Find documentation about watsonx.ai features"
}
</arguments>
</use_mcp_tool>
```

### tavily_map
Map a website's structure to discover available URLs.

**Parameters:**
- `url` (required): Root URL to begin mapping
- `max_depth` (optional): Maximum mapping depth (default: 1, minimum: 1)
- `max_breadth` (optional): Maximum links per page level (default: 20, minimum: 1)
- `limit` (optional): Total links to process (default: 50, minimum: 1)
- `instructions` (optional): Natural language instructions
- `select_paths` (optional): Regex patterns for URL path filtering
- `select_domains` (optional): Regex patterns for domain filtering
- `allow_external` (optional): Return external links (default: true)

**Usage Example:**
```xml
<use_mcp_tool>
<server_name>tavily-remo</server_name>
<tool_name>tavily_map</tool_name>
<arguments>
{
  "url": "https://www.ibm.com/products",
  "max_depth": 2,
  "instructions": "Map all product pages"
}
</arguments>
</use_mcp_tool>
```

### tavily_research
Perform comprehensive research on a topic using multiple sources.

**Parameters:**
- `input` (required): Comprehensive description of the research task
- `model` (optional): Research depth - "mini", "pro", or "auto" (default: "auto")

**Usage Example:**
```xml
<use_mcp_tool>
<server_name>tavily-remo</server_name>
<tool_name>tavily_research</tool_name>
<arguments>
{
  "input": "Research the latest developments in IBM watsonx.ai and its integration with enterprise applications",
  "model": "pro"
}
</arguments>
</use_mcp_tool>
```

## Best Practices

1. **Choose Appropriate Search Depth**:
   - Use "basic" for quick, general searches
   - Use "advanced" for thorough, comprehensive searches
   - Use "fast" for optimized low-latency searches
   - Use "ultra-fast" when speed is critical

2. **Use Time Ranges**: When searching for recent information, specify appropriate time ranges (day, week, month, year)

3. **Domain Filtering**: Use `include_domains` or `exclude_domains` to focus on specific sources or exclude unreliable ones

4. **Extract vs Search**: Use `tavily_extract` when you have specific URLs and need their content, use `tavily_search` for discovery

5. **Research for Complex Topics**: Use `tavily_research` for multi-faceted topics that require synthesizing information from multiple sources

6. **Crawl for Documentation**: Use `tavily_crawl` when you need to explore documentation sites or gather information from multiple related pages

## Response Handling

After receiving search results:
1. **Summarize Key Findings**: Present the most relevant information clearly
2. **Cite Sources**: Include URLs and source information
3. **Assess Recency**: Note the date of information when relevant
4. **Provide Context**: Explain how the findings relate to the user's question
5. **Suggest Follow-ups**: Offer to search for more specific information if needed

## Example Workflows

### Workflow 1: Quick Fact Check
```
User: "Search the internet for the latest IBM CEO"
→ Use tavily_search with basic depth
→ Present current CEO information with source
```

### Workflow 2: Deep Research
```
User: "Research the latest AI regulations in the EU"
→ Use tavily_research with "pro" model
→ Synthesize findings from multiple sources
→ Present comprehensive summary with citations
```

### Workflow 3: Documentation Exploration
```
User: "Find all documentation about IBM watsonx.ai APIs"
→ Use tavily_crawl on IBM docs site
→ Extract relevant API documentation
→ Organize and present findings
```

## Notes
- Rate limit: 20 requests per minute for tavily_research
- Always respect the user's privacy and search intent
- Provide accurate citations and source URLs
- Indicate when information might be time-sensitive or subject to change
