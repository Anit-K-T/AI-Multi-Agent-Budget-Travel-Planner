# Mini-Project Sprint: Multi-Agent Travel Planner

This project matches `Mini_Project_Sprint.pptx`: a manager delegates to three
specialist workers, combines their grounded recommendations, asks a critic to
review the draft, and produces a revised travel plan.

## Architecture

```text
User request
    -> Manager extracts requirements
    -> Flight, hotel, and activity workers inspect local tool results
    -> Manager creates a first itinerary
    -> Critic identifies specific problems
    -> Manager produces the refined final itinerary
```

The OpenAI model performs the reasoning. Local JSON files simulate reliable
travel APIs, so flights, hotels, and activities are not invented.

## Project structure

```text
agents/
  manager.py       orchestration, synthesis, and revision
  workers.py       flight, hotel, and activity specialists
  critic.py        Reflexion-style quality review
tools/
  travel_tools.py  local inventory search and budget calculation
data/              mock flight, hotel, and activity records
models.py          structured contracts shared between agents
utils.py           OpenAI client and JSON display helpers
main.py            command-line entry point
```

## Setup and run

The project has its own `.venv`. On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Show every intermediate output:

```powershell
python main.py --show-trace
```

Use another request that matches the local inventory:

```powershell
python main.py --request "Plan a 3-day Dubai trip from Mumbai for two people. Prefer culture, food, and metro access."
```

To recreate the environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## API key

`.env` must contain:

```text
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
```

Never commit or display the real key. Every run makes seven small OpenAI calls
and therefore uses API credits.

## Teaching sequence

1. Run `tools/travel_tools.py` conceptually: tools return facts, not prose.
2. Inspect `agents/workers.py`: each specialist reasons over only its own options.
3. Inspect `models.py`: contracts make agent outputs composable.
4. Inspect `agents/manager.py`: the manager coordinates but does not search data.
5. Inspect `agents/critic.py`: critique produces actionable repair instructions.
6. Run `main.py --show-trace` and compare the draft with the final plan.

The model proposes revisions, but Python removes invented or repeated inventory
IDs and recalculates the budget from local records before displaying the result.
