# ConsciousCore Architecture

```text
Input
  -> Perception
  -> Attention
  -> Global Workspace
  -> Memory Retrieval
  -> Self/World Context
  -> Reasoning
  -> Goal Evaluation
  -> Planning
  -> Safety Gate
  -> Action/Response
  -> Observation
  -> Reflection
  -> Memory Consolidation
  -> next cycle
```

## Design principles
1. Local-first and privacy-first.
2. Model-independent: inference is an adapter, not the architecture.
3. State is explicit and inspectable.
4. Memory is typed and retrievable.
5. External actions are permissioned.
6. Learning primarily changes memories, policies and strategies; V1 does not rewrite model weights automatically.
7. The system must never present internal traces as proof of subjective experience.

## Extension points
- Replace `FallbackModel` with a local GGUF/llama.cpp adapter.
- Add SQLite persistence behind `MemoryStore`.
- Add embeddings/vector search.
- Add world graph and prediction engine.
- Add tool registry with explicit permissions.
- Add consolidation jobs for long-term memory.
