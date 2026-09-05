# ConsciousCore

**Persistent Memory. Self Model. Attention. Reflection. One Continuous Cognitive System.**

ConsciousCore is a local-first, consciousness-inspired cognitive operating layer for AI systems. It implements persistent memory, attention, a global workspace, internal state, goals, reflection, and a pluggable local-model interface.

> **Scientific boundary:** ConsciousCore does not claim to create subjective consciousness, sentience, self-awareness, or qualia. Terms such as self-model and reflection describe engineered computational mechanisms.

## Current V1 foundation

- FastAPI local runtime
- SQLite persistent memory
- Typed memory: working, episodic, semantic, procedural, self, meta
- Importance and confidence scoring
- Memory retrieval and access tracking
- Memory consolidation endpoint
- Global workspace state
- Internal state: arousal, valence, uncertainty, energy
- Self-model metadata
- Goals API
- Reflection endpoint
- WebSocket event stream
- Local-only deterministic fallback model
- Optional GGUF inference through `llama-cpp-python`
- Local model manager
- CORS configuration through environment variables
- Pytest + pytest-asyncio test foundation
- GitHub Actions CI

## Architecture

```text
Input
  -> Perception
  -> Attention
  -> Global Workspace
  -> Memory Retrieval
  -> Self / World State
  -> Internal State
  -> Goal Evaluation
  -> Reasoning / Model
  -> Planning
  -> Safety
  -> Action / Response
  -> Observation
  -> Reflection
  -> Learning
  -> Memory Consolidation
  -> Loop
```

## Run locally

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The SQLite database is created automatically at `data/consciouscore.db` by default. Set `CONSCIOUSCORE_DB` to choose another local path.

## API

- `GET /health`
- `GET /api/state`
- `POST /api/chat`
- `GET /api/memory`
- `POST /api/memory`
- `POST /api/memory/consolidate`
- `GET /api/self`
- `GET /api/workspace`
- `GET /api/attention`
- `GET /api/goals`
- `POST /api/goals`
- `POST /api/reflection`
- `GET /api/settings`
- `WS /ws/events`

## Local GGUF model

The llama.cpp adapter is optional. Install `llama-cpp-python`, keep GGUF files locally, then register a model through the Python `ModelManager`. No cloud provider or API key is required by the architecture.

## Safety principles

- Local-first by default
- External actions require explicit approval
- No authentication bypass
- No CAPTCHA or MFA bypass
- No password, OTP, cookie, or session-token extraction
- No unrestricted self-modifying code
- Learning starts with memory, strategies, configuration, and evaluation rather than automatic model-weight rewriting

## Development

Run tests with:

```bash
cd backend
PYTHONPATH=. pytest -q
```

The project is intentionally being built in incremental layers. Future modules include richer attention, world modeling, planning, prediction, metacognition, tool permissions, model downloading, backup/restore, analytics, and a complete multi-page UI.
