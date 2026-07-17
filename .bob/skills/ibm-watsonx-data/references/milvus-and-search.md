# Milvus Vector Services & Semantic Search

watsonx.data hosts **Milvus** for vector similarity / RAG. The SDK **manages the
service**; the **`pymilvus` client** does the actual vector work (SKILL.md §6). All
SDK methods take `auth_instance_id=`.

## Manage the Milvus service (SDK)

```python
client.create_milvus_service(... , auth_instance_id=INSTANCE)   # provision a Milvus service
client.list_milvus_services(auth_instance_id=INSTANCE)
client.get_milvus_service(service_id="…", auth_instance_id=INSTANCE)
client.update_milvus_service(...); client.delete_milvus_service(...)
client.create_milvus_service_pause(service_id="…", auth_instance_id=INSTANCE)
client.create_milvus_service_resume(...); client.create_milvus_service_scale(...)
client.update_milvus_service_bucket(...)                        # back the service with a bucket
client.list_milvus_service_databases(service_id="…", auth_instance_id=INSTANCE)
client.list_milvus_database_collections(...); client.list_milvus_database_partitions(...)
```

## Vector work (pymilvus client — not the SDK)

The management SDK does not insert vectors or run searches. Connect the Milvus
client to the running service:

```python
from pymilvus import MilvusClient
mc = MilvusClient(uri="https://<milvus-host>:<grpc-port>", token="<user>:<apikey>")
mc.create_collection(collection_name="docs", dimension=768)
mc.insert(collection_name="docs", data=[{"id": 1, "vector": emb, "text": "…"}])
mc.search(collection_name="docs", data=[query_emb], limit=5, output_fields=["text"])
```
Get the host/port from the Milvus service details (`get_milvus_service`). Patterns:
similarity, scalar-filtered, grouping, **hybrid search with reranking**, and full
RAG pipelines — see the watsonx.data tutorials repo (`Tutorials/`,
`milvus_library/`).

## Semantic search query registry (SDK)

```python
client.create_semantic_search_queries(... , auth_instance_id=INSTANCE)
client.list_semantic_search_queries(auth_instance_id=INSTANCE)
client.delete_semantic_search_queries(...); client.delete_semantic_search_queries_by_id(...)
```
This registers/manages saved semantic-search queries on the platform — distinct
from executing a vector search (which is the `pymilvus` path above).

## RAG note

For retrieval-augmented generation: embed documents → store in a Milvus collection
→ at query time embed the question, `search` for top-k, feed results to an LLM. The
watsonx.data tutorials include end-to-end RAG (PDF/text/image/multi-modal) and
hybrid search with reranking.
