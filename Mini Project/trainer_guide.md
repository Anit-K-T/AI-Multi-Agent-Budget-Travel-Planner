# Trainer Guide: Multi-Agent Travel Planner

## Learning goal

Freshers should understand how a manager-worker architecture decomposes a large
task, grounds decisions in tools, exposes intermediate outputs, and improves a
draft through critique.

## Suggested 120-minute flow

### 1. Frame the problem (10 minutes)

Ask why one large travel-planning prompt is difficult to debug. Introduce the
manager, three specialists, local tools, critic, and final revision.

### 2. Inspect local data and tools (15 minutes)

Open `data/` and `tools/travel_tools.py`.

Explain that the local JSON records simulate travel APIs. The tools only search
records and calculate totals; they do not write the answer or make decisions.

### 3. Explain output contracts (15 minutes)

Open `models.py`. Connect each Pydantic class to slide 9:

- `TravelRequirements` is the manager-to-worker contract.
- `WorkerDecision` is the worker-to-manager contract.
- `DraftItinerary` is the manager-to-critic contract.
- `Critique` is the critic-to-manager contract.
- `FinalItinerary` is the final output contract.

### 4. Walk through one worker (20 minutes)

Open `agents/workers.py` and follow the flight worker:

1. Reason: identify the important constraint.
2. Act: search the local flight data.
3. Observe: inspect matching options.
4. Decide: select an exact ID and explain the trade-off.

Then show that hotel and activity workers use the same small pattern.

### 5. Explain manager orchestration (20 minutes)

Open `agents/manager.py`. Follow `run_pipeline()` from top to bottom. Emphasise
that the manager delegates searches, combines outputs, and verifies that chosen
IDs came from worker results. Python calculates the final budget from local data.

### 6. Add the critic (15 minutes)

Open `agents/critic.py`. The critic checks budget, pacing, preferences,
constraints, and assumptions. It produces repair instructions rather than a
replacement plan.

### 7. Run and inspect (20 minutes)

```powershell
.\.venv\Scripts\Activate.ps1
python main.py --show-trace
```

Ask learners to locate requirement extraction, each worker's contribution, the
first draft, critique, revision changes, and final grounded records.

### 8. Wrap up (5 minutes)

Connect the code to the deck: manager-worker creates boundaries, local tools
provide grounding, ReAct makes worker behavior inspectable, and Reflexion gives
the complete plan a focused second pass.

## Important teaching notes

- The project uses OpenAI for all reasoning; there is no offline heuristic agent.
- Local data remains intentional because the slides recommend mock travel tools
  before introducing changing third-party travel APIs.
- The displayed `reason` is a concise decision summary, not private chain-of-thought.
- Python removes IDs that did not come from worker-selected inventory, removes
  accidental duplicates, and recalculates the final budget from local data.
- A fluent answer is not enough; inspect the trace and grounding.

## Useful questions

**Why not let one prompt do everything?**  
Failures become difficult to locate, constraints can be silently lost, and there
is no clean retry boundary.

**Are the workers separate models?**  
No. They are separate roles and contracts using the same configured model.

**Why retain deterministic tools when everyone has an API key?**  
OpenAI performs reasoning, while local tools provide verifiable travel facts.
This separation is the core architectural lesson.

**Why validate selected IDs in Python?**  
It prevents the language model from introducing flights, hotels, or activities
that were not returned by the tools.

**What changes in production?**  
Replace local search functions with travel API adapters while preserving agent
contracts and orchestration.
