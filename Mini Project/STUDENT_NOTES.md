# Student Notes: Multi-Agent Travel Planner

## 1. What are we building?

We are building a simple travel planner using Python and OpenAI.

The user gives one travel request. For example:

> Plan a four-day Singapore trip from Mumbai for two people. Avoid red-eye
> flights. Keep the hotel cost under ₹45,000. Include food, culture, and views.

The program creates a travel plan for this request.

It does not ask one AI prompt to do everything. It divides the work between
small specialist roles called **agents**.

The project has these agents:

1. **Manager agent** - understands the request and controls the complete process.
2. **Flight worker** - chooses a flight.
3. **Hotel worker** - chooses a hotel.
4. **Activity worker** - chooses activities.
5. **Critic agent** - checks the first travel plan and suggests improvements.
6. **Manager agent again** - uses the critique to create the final plan.

All these roles use the same OpenAI model. They behave differently because each
role receives a different prompt and a different task.

---

## 2. High-level project flow

```text
User travel request
        ↓
Manager extracts clear requirements
        ↓
Local tools find matching travel data
        ↓
Flight, hotel, and activity workers choose options
        ↓
Manager combines the worker results
        ↓
First itinerary is created
        ↓
Critic checks the itinerary
        ↓
Manager improves the itinerary
        ↓
Python validates IDs and calculates the budget
        ↓
Final travel plan is printed
```

---

## 3. Why do we use many agents?

A travel request has many smaller jobs.

- Finding a suitable flight is one job.
- Finding a suitable hotel is another job.
- Selecting activities is another job.
- Combining everything into a good plan is another job.
- Checking the plan is another job.

When one large prompt does all these jobs, it is difficult to find mistakes.

With separate roles, we can check each part:

- Did the flight worker choose a red-eye flight?
- Did the hotel worker respect the hotel budget?
- Did the activity worker choose relevant activities?
- Did the manager create the correct number of days?
- Did the critic find useful problems?

This makes the program easier to understand, test, and improve.

---

## 4. What are tools in this project?

The tools are normal Python functions.

They read local JSON files and return matching records.

For example:

- The flight tool returns flights from Mumbai to Singapore.
- The hotel tool returns hotels in Singapore.
- The activity tool returns activities in Singapore.
- The budget tool adds flight, hotel, and activity costs.

The tools do not use AI. They work with the local data in the `data` folder.

This is important because the OpenAI model should not invent a flight, hotel, or
activity. It must choose from the records returned by the tools.

---

## 5. What is structured output?

Normal AI output is free text. Free text can be difficult for Python to use.

In this project, we tell OpenAI to return information in a fixed structure.

For example, a worker returns fields such as:

```text
worker
reason
action
observation
selected_ids
decision
tradeoffs
```

The structures are defined as Pydantic classes in `models.py`.

Pydantic checks that the expected fields are present and have the correct data
type. This helps different agents share information safely.

---

# 6. Project files

## `main.py`

### Purpose

This is the starting file of the project.

When we run `python main.py`, Python starts here.

This file does not contain the full travel-planning logic. It accepts the user
request, starts the pipeline, and prints the result.

### Important code

#### `DEFAULT_REQUEST`

This is the sample travel request used when the user does not provide another
request.

It asks for:

- A four-day Singapore trip
- Travel from Mumbai
- Two people
- No red-eye flight
- Food, culture, and city views
- Hotel budget below ₹45,000

#### `main()`

This function runs the program.

It performs these steps:

1. Creates the command-line options.
2. Reads the travel request.
3. Calls `run_pipeline()` from the manager file.
4. Prints the final travel plan.
5. Prints the full trace when `--show-trace` is used.

### How to run it

Run with the default request:

```powershell
python main.py
```

Run and show all intermediate results:

```powershell
python main.py --show-trace
```

Run with a different request:

```powershell
python main.py --request "Plan a 3-day Dubai trip from Mumbai for two people."
```

---

## `models.py`

### Purpose

This file defines the structure of the information shared between agents.

Think of each model as a form. The agent must fill all the required fields in
that form.

This file contains classes instead of regular functions.

### `TravelRequirements`

This class stores the user's travel needs.

It includes:

- Origin city
- Destination city
- Number of days
- Number of travellers
- Budget level
- Hotel budget
- Red-eye flight preference
- Travel interests
- Assumptions

The manager creates this object after reading the user's request.

### `WorkerDecision`

This class stores the output from a worker agent.

It includes:

- Worker name
- Short reason summary
- Tool action
- Tool observation
- Selected record IDs
- Final decision
- Trade-offs

The flight, hotel, and activity workers all use this structure.

### `DayPlan`

This class stores the plan for one day.

It includes:

- Day number
- Main focus of the day
- Activity IDs
- Notes

### `BudgetBreakdown`

This class stores the calculated cost.

It includes:

- Flight cost
- Hotel cost
- Activity cost
- Estimated total cost

### `DraftItinerary`

This class stores the manager's first travel plan.

It includes:

- Selected flight ID
- Selected hotel ID
- Day-wise plan
- Budget
- Trade-offs
- Assumptions

### `CritiqueIssue`

This class stores one problem found by the critic.

It includes:

- Severity: low, medium, or high
- Description of the problem
- Instruction to fix the problem

### `Critique`

This class stores the complete critic report.

It includes:

- Overall assessment
- List of issues
- Revision instructions
- Quality score from 0 to 100

### `FinalItinerary`

This class stores the final improved plan.

It contains everything from `DraftItinerary` and also includes:

- Changes made after critique
- Final notes

---

## `utils.py`

### Purpose

This file contains common helper code used by different files.

It loads the API settings, creates the OpenAI client, sends prompts, and formats
the output.

### Important setup code

#### `PROJECT_ROOT`

This stores the location of the project folder.

It helps Python find `.env` and the data files even when the program is started
from another location.

#### `load_dotenv(...)`

This reads the `.env` file.

The `.env` file contains:

```text
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
```

#### `MODEL`

This stores the OpenAI model name.

If `OPENAI_MODEL` is missing, the program uses `gpt-4o-mini`.

#### `client`

This is the OpenAI client object.

The project uses this object to send requests to the OpenAI API.

### `ask_model()`

This is the common function used for every OpenAI call.

It receives:

- A system prompt explaining the agent's role
- A payload containing the input data
- A Pydantic model describing the expected output

It then:

1. Sends the prompt and data to OpenAI.
2. Requests structured output.
3. Parses the output into the requested Pydantic model.
4. Returns the structured result.

If OpenAI does not return the expected output, the function raises an error.

### `pretty_json()`

This function makes dictionaries and Pydantic objects easy to read in the
terminal.

It adds indentation and keeps characters such as the ₹ symbol readable.

---

## `tools/travel_tools.py`

### Purpose

This file contains the local travel tools.

The tools use the JSON files inside the `data` folder.

They provide facts to the worker agents.

### `_read_json()`

This is a small internal helper function.

It receives a JSON filename, reads the file, and converts the JSON data into a
Python list.

The underscore at the beginning means that it is mainly used inside this file.

### `load_travel_data()`

This function loads all three datasets:

- Flights
- Hotels
- Activities

It returns one dictionary containing all the travel data.

### `search_flights()`

This function finds flights that match:

- The origin city
- The destination city

It does not choose the best flight. It only returns matching records. The flight
worker makes the final choice.

### `search_hotels()`

This function finds hotels in the destination city.

It also:

1. Calculates the number of hotel nights.
2. Calculates the total hotel cost for the stay.
3. Adds these values to each hotel option.

It does not choose the hotel. The hotel worker makes that decision.

### `search_activities()`

This function finds activities in the destination city.

It returns the matching local activity records to the activity worker.

### `estimate_budget()`

This function calculates the trip cost using the selected records.

It calculates:

- Flight price multiplied by the number of travellers
- Total hotel price
- Activity prices multiplied by the number of travellers
- Complete estimated total

The model does not control the final arithmetic. Python calculates it from the
local data.

---

## `agents/workers.py`

### Purpose

This file contains the three specialist workers.

Each worker follows the same simple pattern:

```text
Reason → Act → Observe → Decide
```

This is a simple ReAct-style flow.

### `_run_worker()`

This is the common helper used by all three workers.

It receives:

- Worker name
- Worker task
- Travel requirements
- Tool results
- Name of the ID field

It performs these steps:

1. Checks that the tool returned options.
2. Sends the requirements and tool results to OpenAI.
3. Asks the worker to select exact record IDs.
4. Checks whether the selected IDs exist in the tool results.
5. Returns the worker trace, tool results, and selected records.

This function prevents the worker from successfully selecting an invented ID.

### `run_flight_worker()`

This function runs the flight worker.

It:

1. Calls `search_flights()`.
2. Gives matching flights to the OpenAI model.
3. Asks the model to consider route, timing, cost, and red-eye preference.
4. Returns one selected flight and its explanation.

### `run_hotel_worker()`

This function runs the hotel worker.

It:

1. Calls `search_hotels()`.
2. Gives matching hotels to the OpenAI model.
3. Asks the model to consider full-stay price, location, and preferences.
4. Returns one selected hotel and its explanation.

### `run_activity_worker()`

This function runs the activity worker.

It:

1. Calls `search_activities()`.
2. Gives matching activities to the OpenAI model.
3. Asks the model to select up to five varied activities.
4. Returns the selected activities and its explanation.

---

## `agents/critic.py`

### Purpose

This file contains the critic agent.

The critic does not create a new itinerary. It checks the manager's first draft
and gives clear repair instructions.

This is the Reflexion part of the project.

### `critique_itinerary()`

This function receives:

- Travel requirements
- First draft itinerary
- Worker outputs

It asks the OpenAI model to check:

- Budget
- Daily pacing
- User preferences
- Hard constraints
- Unsupported assumptions
- Whether the plan uses worker results

It returns a structured `Critique` object containing issues, fixes, and a quality
score.

---

## `agents/manager.py`

### Purpose

This is the main orchestration file.

The manager controls the complete flow. It gives work to specialists, combines
their outputs, sends the draft to the critic, and creates the final answer.

### `extract_requirements()`

This function reads the user's natural-language request.

It asks OpenAI to convert that request into a `TravelRequirements` object.

For example:

```text
"four-day trip"       → duration_days = 4
"from Mumbai"         → origin = Mumbai
"to Singapore"        → destination = Singapore
"for two people"      → traveller_count = 2
"avoid red-eye"       → avoid_red_eye = true
```

### `_selected_inventory()`

This internal helper collects the options selected by the workers.

It returns:

- One flight
- One hotel
- Selected activities

### `_manager_context()`

This internal helper prepares a smaller and safer input for the manager.

It gives the manager only:

- Worker decisions
- Worker trade-offs
- Worker-approved records

It does not give the manager rejected options. This reduces confusion and helps
the manager stay grounded.

### `_ground_itinerary()`

This internal function validates the itinerary.

It checks:

- The flight ID came from the flight worker.
- The hotel ID came from the hotel worker.
- Activity IDs came from the activity worker.
- No activity appears more than once.
- The number of day blocks matches the trip duration.

It also replaces the model's budget with the amount calculated by Python.

### `_repair_final_inventory()`

This internal function protects the final output from common model mistakes.

It:

- Restores the worker-selected flight if the model changes it.
- Restores the worker-selected hotel if the model changes it.
- Removes invented activity IDs.
- Removes repeated activity IDs.
- Records these corrections in the final change list.

The model still creates the travel plan. Python only protects the factual links
to the local inventory.

### `create_draft()`

This function creates the first itinerary.

It gives OpenAI:

- Extracted requirements
- Worker decisions
- Worker-selected records

It asks the manager to:

- Create one plan block for each day
- Use only selected IDs
- Keep arrival and departure days lighter
- Avoid repeating activities
- Explain trade-offs
- State assumptions

The result is a `DraftItinerary` object.

### `refine_itinerary()`

This function improves the first itinerary.

It gives OpenAI:

- Requirements
- First draft
- Critic report
- Worker-approved options

It asks the manager to fix the critic's issues while preserving the good parts.

After OpenAI responds, Python repairs and validates the inventory IDs and
recalculates the budget.

The result is a `FinalItinerary` object.

### `_display_plan()`

The model uses short IDs such as `SQ-421` and `SG-H01`.

This internal function replaces those IDs with the complete local records so
students can see:

- Flight details
- Hotel details
- Activity names and costs
- Final budget
- Trade-offs
- Assumptions
- Changes after critique

### `run_pipeline()`

This is the most important orchestration function.

It runs the complete project in this order:

1. Load local travel data.
2. Extract user requirements.
3. Run the flight worker.
4. Run the hotel worker.
5. Run the activity worker.
6. Create the first itinerary.
7. Ask the critic to review it.
8. Refine the itinerary.
9. Prepare the readable final output.
10. Return the complete trace.

`main.py` calls this function.

---

## `agents/__init__.py`

This small file marks the `agents` folder as a Python package.

It helps Python import files such as:

```python
from agents.manager import run_pipeline
```

---

## `tools/__init__.py`

This small file marks the `tools` folder as a Python package.

It helps Python import files such as:

```python
from tools.travel_tools import search_flights
```

---

# 7. Non-Python files

## `.env`

This file stores the private OpenAI API key and model name.

Do not display it, share it, or commit it to Git.

## `.env.example`

This is a safe example showing which environment variables are required. It
does not contain the real key.

## `requirements.txt`

This file lists the Python packages required by the project:

- `openai` - communicates with the OpenAI API
- `python-dotenv` - reads the `.env` file
- `pydantic` - defines and validates structured agent outputs

## `data/sample_flights.json`

This file contains mock flight inventory.

## `data/sample_hotels.json`

This file contains mock hotel inventory.

## `data/sample_activities.json`

This file contains mock activity inventory.

## `Mini_Project_Sprint.pptx`

This is the theory presentation for the project.

It explains manager-worker architecture, tools, ReAct, Reflexion, contracts,
grounding, and debugging.

---

# 8. OpenAI calls made during one run

A normal run makes seven OpenAI calls:

1. Manager extracts requirements.
2. Flight worker chooses a flight.
3. Hotel worker chooses a hotel.
4. Activity worker chooses activities.
5. Manager creates the first itinerary.
6. Critic reviews the itinerary.
7. Manager creates the final itinerary.

The local search and budget functions do not call OpenAI.

---

# 9. ReAct in this project

ReAct means **Reason and Act**.

In each worker:

- **Reason** - understand what is important.
- **Act** - use a local search tool.
- **Observe** - look at the returned records.
- **Decide** - select an option and explain the trade-off.

The project stores a short summary of these steps. It does not request or expose
private chain-of-thought.

---

# 10. Reflexion in this project

Reflexion means reviewing an earlier attempt and using feedback to improve the
next attempt.

In this project:

```text
First itinerary
      ↓
Critic finds problems
      ↓
Critic gives repair instructions
      ↓
Manager creates an improved itinerary
```

The final output also lists the changes made after critique.

---

# 11. Important learning points

1. A large problem can be divided into smaller specialist tasks.
2. Every agent should have one clear responsibility.
3. Tools provide facts; models provide reasoning and explanations.
4. Structured output helps agents communicate with each other.
5. The manager coordinates work but should not invent inventory.
6. A critic should give specific fixes, not vague feedback.
7. Python should validate important model outputs.
8. Cost calculations should use code and real data, not model guesses.
9. A trace helps us find which part of the pipeline made a mistake.
10. A fluent answer is not enough; the answer must also be grounded and correct.

---

# 12. Quick classroom revision

| Question | Simple answer |
|---|---|
| What starts the project? | `main.py` |
| Who controls the workflow? | The manager |
| Who chooses the flight? | The flight worker |
| Who chooses the hotel? | The hotel worker |
| Who chooses activities? | The activity worker |
| Where do travel facts come from? | Local JSON data through tools |
| Who checks the first itinerary? | The critic |
| What is ReAct here? | Reason, use a tool, observe, and decide |
| What is Reflexion here? | Critique the first plan and improve it |
| What validates agent output? | Pydantic and Python checks |
| Who calculates the budget? | Python |
| How many OpenAI calls are made? | Seven |

---

# 13. Final one-line summary

This project uses one manager, three specialist workers, local data tools, and
one critic to create a grounded travel plan and improve it before showing it to
the user.
