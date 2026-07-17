# RAG integration

Docling is built for retrieval pipelines: convert → chunk (heading-aware) →
embed → store. This skill's `scripts/docling_chunk.py` emits JSONL you can load
into any vector DB; the recipes below cover the popular frameworks and the MCP
server for agentic use.

## 1. Skill script → JSONL → any vector DB

```bash
python3 scripts/docling_chunk.py report.pdf -o chunks.jsonl --max-tokens 512
```

Each line: `{id, text, raw_text, headings, page_numbers, source, token_count}`.
Embed the `text` field (it's already contextualized with the heading breadcrumb).

```python
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
records = [json.loads(l) for l in open("chunks.jsonl")]
vectors = model.encode([r["text"] for r in records])
# upsert (id, vector, metadata=r) into Chroma / Qdrant / pgvector / Pinecone / Milvus ...
```

### Chroma example

```python
import chromadb, json
client = chromadb.PersistentClient(path="./chroma")
col = client.get_or_create_collection("docs")
recs = [json.loads(l) for l in open("chunks.jsonl")]
col.add(
    ids=[r["id"] for r in recs],
    documents=[r["text"] for r in recs],
    metadatas=[{"source": r["source"], "headings": " > ".join(r["headings"]),
                "pages": ",".join(map(str, r["page_numbers"]))} for r in recs],
)
```

### Qdrant example

```python
import json, uuid
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
recs = [json.loads(l) for l in open("chunks.jsonl")]
vecs = model.encode([r["text"] for r in recs])
qc = QdrantClient(":memory:")
qc.recreate_collection("docs", vectors_config=VectorParams(size=len(vecs[0]), distance=Distance.COSINE))
qc.upsert("docs", [PointStruct(id=str(uuid.uuid4()), vector=v.tolist(), payload=r)
                   for v, r in zip(vecs, recs)])
```

## 2. Chunking directly in Python (HybridChunker)

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer

doc = DocumentConverter().convert("report.pdf").document
tokenizer = HuggingFaceTokenizer.from_pretrained(
    model_name="sentence-transformers/all-MiniLM-L6-v2", max_tokens=512,
)
chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
for chunk in chunker.chunk(dl_doc=doc):
    embed_text = chunker.contextualize(chunk=chunk)   # heading breadcrumb + text
    print(chunk.meta.headings, chunk.meta.origin.filename)
```

OpenAI tokenizer (for OpenAI embedding models):

```python
import tiktoken
from docling_core.transforms.chunker.tokenizer.openai import OpenAITokenizer
tokenizer = OpenAITokenizer(
    tokenizer=tiktoken.encoding_for_model("text-embedding-3-small"), max_tokens=8192,
)   # pip install 'docling-core[chunking-openai]'
```

## 3. LangChain

```python
# pip install langchain-docling
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType

loader = DoclingLoader(
    file_path=["report.pdf", "https://arxiv.org/pdf/2408.09869"],
    export_type=ExportType.DOC_CHUNKS,   # or ExportType.MARKDOWN
)
docs = loader.load()                     # LangChain Documents with heading metadata
```

## 4. LlamaIndex

```python
# pip install llama-index-readers-docling llama-index-node-parser-docling
from llama_index.readers.docling import DoclingReader
from llama_index.node_parser.docling import DoclingNodeParser

reader = DoclingReader()                 # yields JSON DoclingDocuments by default
nodes = DoclingNodeParser().get_nodes_from_documents(reader.load_data("paper.pdf"))
```

## 5. Haystack

```python
# pip install docling-haystack haystack-ai
from docling_haystack.converter import DoclingConverter
converter = DoclingConverter()           # emits Haystack Documents (chunked)
```

## 6. MCP server (agentic use)

Docling ships an official MCP server (`docling-mcp`, repo
`docling-project/docling-mcp`) exposing conversion/chunking as tools an agent can
call. The launch command changes between releases — check the repo README for the
current `docling-mcp` invocation and add it to your MCP client config.

## Chunking guidance

- **Embed `contextualize()` output**, not the raw chunk — the prepended heading
  path is what makes retrieval land on the right section.
- Match `--max-tokens` to your embedding model's window (MiniLM 512;
  `text-embedding-3-*` up to 8192).
- Use `--strategy hierarchical` when you want structure-faithful splits and will
  handle token limits downstream yourself.
- Keep `page_numbers` in metadata so citations can point back to the source page.
