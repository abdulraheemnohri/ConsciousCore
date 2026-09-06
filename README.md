# ConsciousCore

**Persistent Memory · Self Model · World Model · Global Workspace · Reflection · Learning · Autobiographical Timeline · Local/Cloud/Remote/Hybrid/Parallel Runtime**

ConsciousCore is a local-first, consciousness-inspired cognitive operating layer for AI systems. It combines persistent memory, attention, global-workspace coordination, internal computational state, goals, planning, safety, prediction, metacognition, reflection, bounded learning, event history, autobiographical-style episode storage, and pluggable model/runtime inference.

> **Scientific boundary:** ConsciousCore does not claim to create subjective consciousness, sentience, qualia, or proof of experience. Self-model, internal-state, reflection, global-workspace, and autobiographical terms describe engineered computational mechanisms.

## Runtime architecture

ConsciousCore now defines a provider-neutral runtime layer for:

- **Solo Local** — local model + local cognitive state
- **Solo Cloud** — optional cloud model execution
- **Solo Remote** — self-hosted model server
- **Hybrid** — local cognitive state with optional cloud/remote generation
- **Parallel** — multiple enabled providers can produce candidate results
- **Distributed** — multiple runtime nodes can participate
- **Auto** — policy selects a safe route based on privacy and availability

The runtime is intentionally separate from the cognitive state. Models provide generation/embedding/vision capabilities; ConsciousCore owns continuity, memory, workspace, goals, self/world models, safety, reflection and learning.

## Privacy boundary

Data is classified as `public`, `internal`, `private`, `sensitive`, or `secret`. Remote/cloud execution is opt-in and policy checked. Secret-like material is blocked from cloud routing and can be redacted before remote use. Local-only operation remains the default.

## Memory federation

Memory can be configured as local-only, local+remote, local+cloud, or other explicitly selected replication policies. Future sync services can use the runtime contracts without coupling the cognitive engine to one vendor.

## Telemetry

Remote telemetry is disabled by default. Local diagnostics may remain enabled for CPU/RAM/GPU, latency, errors and subsystem health. No cloud telemetry is required for core operation.

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
 → Runtime Selection
 → Local / Cloud / Remote / Hybrid / Parallel
 → Reasoning / Model
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
- Observable cognitive loop with cycle IDs
- Typed persistent memory with importance/confidence, retrieval, update/delete and consolidation
- Attention ranking and metacognitive confidence/uncertainty
- Global Workspace V2 with candidate competition, winner selection, broadcast, interruption and subscriptions
- World Model V2 with entities, properties, temporal relations, events, beliefs, history, queries and contradiction detection
- Goals and persistent plans with step dependencies and lifecycle controls
- Reflection and bounded Learning V2 with lessons, strategies, evidence and recommendations
- Cognitive Event Bus V2 with persistent timeline, filters, cycle/phase queries, correlation IDs and parent IDs
- Autobiographical Memory V2 with episodes, timeline, search, archive, statistics and links to cycles/plans/reflections/learning
- Self Model V2 with capabilities, limitations, autonomy and explicit scientific boundaries
- Internal computational state with energy, arousal, attention load, stress, uncertainty, confidence and stability
- Safety engine with autonomy levels 0–3 and approval-gated execution
- Prohibited actions: authentication bypass, secret extraction, credential capture, MFA/CAPTCHA bypass and destructive system changes
- Local GGUF model manager and optional llama.cpp adapter
- Deterministic fallback model when no local model is available
- Provider-neutral runtime router for local/cloud/remote/hybrid/parallel/distributed modes
- Privacy-aware data boundary classification
- Persistent runtime settings and immutable safety invariants
- WebSocket event stream
- Audit log
- Responsive frontend control center

## Runtime configuration

Copy `config/runtime.example.json` to a private runtime configuration file and adjust it for your deployment. Do not commit real API keys or credentials. Prefer environment variables for secrets.

## Run locally

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
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

## Testing

```bash
cd backend
PYTHONPATH=. pytest -q
```

The runtime routing tests cover secret blocking, local fallback, hybrid routing and parallel candidates.

## Safety and autonomy

- Local-first by default
- No cloud inference is required by the architecture
- External actions require explicit approval
- Execution engine is a local simulation/state-transition layer unless a future, separately approved integration is added
- No password, OTP, cookie or session-token extraction
- No authentication, MFA or CAPTCHA bypass
- No unrestricted self-modifying source code
- Learning changes bounded memory/strategy/configuration, not model weights automatically
