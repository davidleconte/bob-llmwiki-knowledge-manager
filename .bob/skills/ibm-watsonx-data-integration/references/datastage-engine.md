# DataStage Parallel Engine — Knowledge & Optimization

Conceptual reference for the DataStage parallel engine and flow optimization
(SKILL.md §7). Use for "why/how does the engine behave" questions and for tuning,
independent of the authoring tool. For exact stage semantics and properties, use
`recommend_datastage_stages` / `datastage_property_lookup` (or the per-stage
knowledge files in the IBM skills repo).

## When to use DataStage

Batch ETL of large volumes; parallel processing across nodes; complex
high-throughput transformations; enterprise DB/file integration; data-warehouse
loading and CDC.

## Engine characteristics

- **Partition parallelism** — data is divided into partitions processed
  simultaneously across nodes.
- **Pipeline parallelism** — multiple stages process different data concurrently.
- **Scalable** — add nodes to increase throughput.

## Key concepts

- **Partitioning** — data divided across processing nodes.
- **Nodes** — physical/logical processing units.
- **Partitions** — independently processed subsets of data.
- **Configuration (APT) file** — defines nodes and resources.

Performance is governed by job design (stage selection, partitioning, data flow),
configuration (node/partition count, resources), and infrastructure (disk I/O,
network, CPU).

## Flow optimization

**When:** complex multi-stage flows, millions+ rows, long run times, after initial
development/testing.

**Partitioning**
- Hash on keys for grouping stages (Aggregator, Join, Sort, Remove Duplicates).
- Use **Same** to preserve upstream partitioning (zero overhead).
- Avoid unnecessary repartitioning.

**Sorting**
- Minimize sorts (expensive); leverage pre-sorted data; use sort-merge collectors
  strategically.

**Stage selection**
- Prefer Transformer over Filter/Switch; use Copy for type conversion only; remove
  unnecessary stages; use Data Sets for inter-job communication; combine back-to-back
  Transformers.

**Performance tuning**
- Adjust buffer sizes / memory limits; configure degree of parallelism; optimize
  DB bulk loading; choose appropriate file formats.

**Workflow:** verify correctness first → identify bottlenecks (sorts,
repartitioning, heavy stages) → apply techniques → measure → document.

## Deeper topics (in the IBM knowledge skill)

Concurrent job execution, configuration management, dataset performance, disk &
resource optimization, restart & recovery, and detailed partitioning / sorting /
memory-management guidelines live in
`di-agent-knowledge-engine-datastage/` (engine details + `optimization/`). Consult
those for specifics; this file is the orientation map.
