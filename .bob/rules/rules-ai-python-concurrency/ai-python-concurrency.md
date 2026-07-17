# Python Concurrency & Performance
<!-- Owner: EMEA Bob program · Last-reviewed: 2026-06-10 · Scope: global · Persona: AI Engineer -->

## Default model
- I/O-bound work (LLM calls, HTTP, DB): use async I/O (`asyncio` + async clients).
- CPU-bound work: do NOT use threads — the GIL serializes them. Use
  `ProcessPoolExecutor` or offload to a worker.

## Never block the event loop
- No synchronous SDK/HTTP/DB call inside an `async def`. Use the async client, or
  `loop.run_in_executor()` for unavoidable sync code.
- No `time.sleep()` in async paths — use `await asyncio.sleep()`.

## Bound and protect
- Cap fan-out (parallel LLM/API calls) with an `asyncio.Semaphore`; respect provider rate limits.
- Set an explicit timeout on every network call. No unbounded awaits.
- Stream large responses/datasets; never buffer a whole result set in memory.
