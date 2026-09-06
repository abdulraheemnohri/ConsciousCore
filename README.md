# ConsciousCore

**Persistent Memory · Self Model · World Model · Global Workspace · Reflection · Learning · Autobiographical Timeline**

ConsciousCore is a local-first, consciousness-inspired cognitive operating layer for AI systems. It combines persistent memory, attention, global-workspace coordination, internal computational state, goals, planning, safety, prediction, metacognition, reflection, bounded learning, event history, autobiographical-style episode storage, and pluggable local model inference.

> **Scientific boundary:** ConsciousCore does not claim to create subjective consciousness, sentience, qualia, or proof of experience. Self-model, internal-state, reflection, global-workspace, and autobiographical terms describe engineered computational mechanisms.

## Implemented architecture

```text
Input
 → Perception
 → Attention
 → Global Workspace V2
 → Memory Retrieval
 → Self Model V2 / World Model V2
 → Internal State V3
 → Goal Evaluation
 → Reasoning / Local Model
 → Planning
 → Safety + Approval Gate
 → Local Simulation / Response
 → Observation
 → Reflection
 → Learning V2
 → Memory Consolidation
 → Autobiographical Memory V2
 → Cognitive Event Bus V2
 → Loop
```

## Core features

- FastAPI local runtime + SQLite persistence
- Cognitive Loop with observable phases and cycle IDs
- Typed persistent memory with importance/confidence, retrieval, update/delete and consolidation
- Attention ranking and metacognitive confidence/uncertainty
- Global Workspace V2 with candidate competition, winner selection, broadcast, interruption and subscriptions
- World Model V2 with entities, properties, temporal relations, events, beliefs, history, queries and heuristic contradiction detection
- Goals and persistent plans with step dependencies and lifecycle controls
- Reflection and bounded Learning V2 with lessons, strategies, evidence and recommendations
- Cognitive Event Bus V2 with persistent timeline, filters, cycle/phase queries, correlation IDs and parent IDs
- Autobiographical Memory V2 with persistent cognitive episodes, timeline, search, archive, statistics and links to cycles/plans/reflections/learning
- Self Model V2 with capabilities, limitations, autonomy and explicit scientific boundaries
- Internal computational state with energy, arousal, attention load, stress, uncertainty, confidence and stability
- Safety engine with autonomy levels 0–3 and approval-gated execution
- Prohibited actions: authentication bypass, secret extraction, credential capture, MFA/CAPTCHA bypass and destructive system changes
- Local GGUF model manager and optional llama.cpp adapter
- Deterministic fallback model when no local model is available
- Persistent runtime Settings V2 with bounded controls and immutable safety invariants
- WebSocket event stream
- Audit log
- Unified responsive frontend control center with dashboard, chat, loop, memory, goals, planner, world model, workspace, events, learning, autobiographical timeline, self model, state, safety, models, sleep, tools, settings and audit views

## Runtime settings

Settings are local and persisted in SQLite. Supported controls include autonomy level, memory enablement/limits, attention, global workspace, reflection, prediction, planning, bounded learning, autobiographical memory and event-history limits. Safety invariants remain enabled and cannot be changed through the settings layer.

## Autobiographical Memory V2 API

The runtime exposes an extension router under `/api/autobiographical/v2`:

- `GET /api/autobiographical/v2`
- `GET /api/autobiographical/v2/episodes`
- `GET /api/autobiographical/v2/episodes/{id}`
- `POST /api/autobiographical/v2/episodes`
- `GET /api/autobiographical/v2/search`
- `GET /api/autobiographical/v2/timeline`
- `GET /api/autobiographical/v2/stats`
- `PATCH /api/autobiographical/v2/episodes/{id}/archive`

## Settings V2 API

- `GET /api/settings/v2`
- `PATCH /api/settings/v2`
- `POST /api/settings/v2/reset`

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

SQLite is created automatically at `data/consciouscore.db` by default. Set `CONSCIOUSCORE_DB` for another local path.

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` when the backend is not on `http://127.0.0.1:8000`.

## Safety and autonomy

- Local-first by default
- No cloud inference is required by the architecture
- External actions require explicit approval
- Execution engine is a local simulation/state-transition layer unless a future, separately approved integration is added
- No password, OTP, cookie or session-token extraction
- No authentication, MFA or CAPTCHA bypass
- No unrestricted self-modifying source code
- Learning changes bounded memory/strategy/configuration, not model weights automatically

## Testing

```bash
cd backend
PYTHONPATH=. pytest -q
```

Remote GitHub status checks are not treated as proof of passing tests unless GitHub reports an actual check result.
