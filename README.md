# ConsciousCore V1

**Local-First Universal Cognitive Operating Layer**

> **Tagline:** Persistent Memory. Self Model. Attention. Reflection. One Continuous Cognitive System.

---

## Scientific Position & Identity

> ⚠️ **Scientific Position:** ConsciousCore **MUST NOT** claim to be genuinely conscious, sentient, self-aware in the phenomenal sense, or capable of subjective experience.
>
> ConsciousCore is defined scientifically as a **"consciousness-inspired cognitive architecture"** or **"functional cognitive continuity layer."**
>
> The system models functions commonly associated with consciousness research—attention, working memory, self-modeling, global workspace, reflection, prediction, goal management, metacognition, and continuity—without asserting subjective experience.

---

## Product Vision & Principles

ConsciousCore sits above AI models and below applications/tools. The AI model is **replaceable**; ConsciousCore owns the persistent functional state and cognitive orchestration.

### Core Principles
1. **Local-First & Offline Capable:** Complete processing on local device/server with fallback options.
2. **Privacy & Data Boundary Protection:** Automatic classification (`PUBLIC`, `INTERNAL`, `PRIVATE`, `SENSITIVE`, `SECRET`) and local secret redaction.
3. **Model Independence:** Replaceable local, cloud, remote, or parallel model backends (Ollama, vLLM, llama.cpp, GGUF, OpenAI-compatible).
4. **Observable Cognition:** Transparent Global Workspace V2, decision summaries, and execution inspection.
5. **Bounded Autonomy & Safety:** Immutable safety rules, approval-gated actions, no secret extraction or silent remote exfiltration.

---

## Fundamental Architecture

```
                    USER / APPLICATION
                           │
                           ▼
                     PERCEPTION
                           │
                           ▼
                  EVENT NORMALIZATION
                           │
                           ▼
                  GLOBAL WORKSPACE
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
         ATTENTION                  INTERNAL STATE
             │                           │
             └─────────────┬─────────────┘
                           ▼
                    MEMORY ROUTER
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   LOCAL MEMORY       CLOUD MEMORY       REMOTE MEMORY
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                      SELF MODEL
                           │
                           ▼
                      WORLD MODEL
                           │
                           ▼
                     GOAL EVALUATION
                           │
                           ▼
                       REASONING
                           │
                           ▼
                       PLANNING
                           │
                           ▼
                    MODEL ORCHESTRATOR
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
      LOCAL              CLOUD              REMOTE
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ▼
                      SAFETY ENGINE
                           │
                           ▼
                     TOOL EXECUTION
                           │
                           ▼
                      OBSERVATION
                           │
                           ▼
                      REFLECTION
                           │
                           ▼
                       LEARNING
                           │
                           ▼
                  MEMORY CONSOLIDATION
                           │
                           ▼
                    STATE UPDATE
                           │
                           └──────────► NEXT CYCLE
```

---

## UI Control Center & Screenshots

ConsciousCore V1 provides a comprehensive React + TypeScript Control Center with 28 specialized UI pages and `Ctrl+K` Command Palette navigation.

### Core Workspace
| Page | Preview |
| --- | --- |
| **Dashboard** | ![Dashboard](assets/screenshots/dashboard.png) |
| **Chat Workspace** | ![Chat Workspace](assets/screenshots/chat_workspace.png) |
| **Global Workspace V2** | ![Global Workspace](assets/screenshots/global_workspace.png) |
| **Attention Center** | ![Attention Center](assets/screenshots/attention_center.png) |

---

### Memory & State Management
| Page | Preview |
| --- | --- |
| **Memory Center** | ![Memory Center](assets/screenshots/memory.png) |
| **Memory Federation & Sync** | ![Memory Federation](assets/screenshots/memory_federation.png) |
| **Self Model V2** | ![Self Model](assets/screenshots/self_model.png) |
| **World Model V2** | ![World Model](assets/screenshots/world_model.png) |
| **Internal Computational State** | ![Internal State](assets/screenshots/internal_state.png) |

---

### Planning, Reasoning & Cognition
| Page | Preview |
| --- | --- |
| **Goals Engine** | ![Goals Engine](assets/screenshots/goals.png) |
| **Planner & Kanban** | ![Planner](assets/screenshots/planner.png) |
| **Reasoning Center** | ![Reasoning Center](assets/screenshots/reasoning.png) |
| **Reflection Engine** | ![Reflection Engine](assets/screenshots/reflection.png) |
| **Metacognition** | ![Metacognition](assets/screenshots/metacognition.png) |
| **Prediction Engine** | ![Prediction Engine](assets/screenshots/prediction.png) |
| **Simulation Sandbox** | ![Simulation Sandbox](assets/screenshots/simulation.png) |
| **Sleep / Consolidation** | ![Sleep Maintenance](assets/screenshots/sleep.png) |

---

### Runtime & AI Engine
| Page | Preview |
| --- | --- |
| **Runtime Center** | ![Runtime Center](assets/screenshots/runtime_center.png) |
| **Model Manager** | ![Model Manager](assets/screenshots/models.png) |
| **Parallel AI Strategies** | ![Parallel AI](assets/screenshots/parallel_ai.png) |
| **Distributed Nodes** | ![Distributed Nodes](assets/screenshots/distributed_nodes.png) |

---

### System, Safety & Operations
| Page | Preview |
| --- | --- |
| **Tool Center** | ![Tool Center](assets/screenshots/tools.png) |
| **Safety Engine & Approvals** | ![Safety Center](assets/screenshots/safety.png) |
| **Telemetry Center** | ![Telemetry Center](assets/screenshots/telemetry.png) |
| **Analytics** | ![Analytics](assets/screenshots/analytics.png) |
| **System Audit Logs** | ![System Logs](assets/screenshots/logs.png) |
| **Developer Console** | ![Developer Console](assets/screenshots/developer_console.png) |
| **Settings Center** | ![Settings](assets/screenshots/settings.png) |

---

## Universal Runtime Modes

- **Local:** On-device model, memory, safety, and tools.
- **Cloud:** Disabled by default; policy-gated generation.
- **Remote:** Connects to Ollama, vLLM, llama.cpp, TGI, or custom remote endpoints.
- **Hybrid (Recommended):** Local memory, workspace, safety, self-model + Remote specialist inference.
- **Parallel:** Concurrent execution using **Race**, **Judge**, **Consensus**, **Specialist**, or **Debate** strategies.
- **Distributed:** Multi-node coordination with memory replication and workload distribution.

---

## Memory System & Federation

ConsciousCore manages 7 distinct memory types:
1. **Working Memory:** Active context budget.
2. **Episodic Memory:** Specific cognitive experiences.
3. **Semantic Memory:** Knowledge and factual network.
4. **Procedural Memory:** Skills, workflows, and procedures.
5. **Self Memory:** Functional self-model state.
6. **Meta Memory:** Uncertainty, reliability, and error history.
7. **Autobiographical Memory:** Timeline of cognitive episodes.

---

## Quick Start & Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- SQLite3

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. Use `Ctrl + K` to open the Command Palette.

---

## API & Documentation

Interactive API documentation is generated automatically by FastAPI:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`

---

## License

ConsciousCore V1 is released under the Apache 2.0 License.
