# Blueprint-Generator — STEPS

Progressive learning steps for the `blueprint-generator` project (idea → structured blueprint).
Each row records a completed increment with its one-sentence summary, the architectural choices made, and why.

| Step | Name | Summary | Key Concepts (choices + why) |
| --- | --- | --- | --- |
| 1 | Project foundation | Initialize the `blueprint-generator` project with `uv`, a virtual environment, dependencies, `.env`/`.env.example`, `.gitignore`, and Git. | **`uv` + `pyproject.toml`** for reproducible, lockfile-pinned dependencies — one source of truth; **`.env` over hardcoded secrets** so keys never enter the repo; **`.gitignore`** keeps the environment/secrets out of version control; **early Git** so every increment is reviewable and reversible. |
| 2 | Initial application structure | Scaffold the minimal module layout (`app.py`, `generator.py`, `schemas.py`, `prompts.py`) so each future concern has a home. | **One concern per module** (CLI, generation, schema, prompts) — the skeleton defines the boundaries the architecture will respect later; **CLI as entrypoint** keeps everything runnable from day one; deliberately minimal, so nothing is scaffolded before it earns a home. |
| 3 | Pydantic Blueprint schema | Define the first structured output model `ProjectBlueprint` with `project_name` and `business_outcome`. | **Schema-as-contract**: the output shape is decided up front, so the LLM is bound to a known structure instead of returning free text — the schema is the interface both the model and the app agree on. |
| 4 | Schema field validation | Add field descriptions and `field_validator` rules that strip whitespace and reject empty values. | **Typing + validation at the boundary**: rules are enforced by Python (deterministic) not the LLM (probabilistic); **fail-fast** on malformed data keeps bad output from flowing downstream. |
| 5 | OpenRouter connection | Set up the `ProjectGenerator` to send a project idea to OpenRouter via the OpenAI SDK. | **Provider abstraction behind a client**: nothing app-level touches the HTTP API directly, so the model/provider is a swappable detail; API keys supplied via settings, never in code. |
| 6 | Prompt engineering v1 | Build `SYSTEM_PROMPT` and `build_user_prompt()` that frame the LLM's role and task. | **System vs user prompt split**: stable instructions (role, constraints) live in the system prompt; variable input (the idea) lives in the user prompt — separates *what never changes* from *what always changes*. |
| 7 | LangChain OpenRouter client | Move to LangChain's `ChatOpenAI` with message tuples and a `SecretStr` API key for OpenRouter. | **Standardized LLM abstraction**: using LangChain's `ChatOpenAI` (not the raw SDK) so provider specifics (message format, invocation) come from a maintained library; **`SecretStr`** so the key is redacted on printing. |
| 8 | Structured LLM output | Use `with_structured_output(ProjectBlueprint)` so the LLM returns a typed Pydantic object. | **LLM constrained to the schema**: structured output makes the model return valid data the app can trust without brittle parsing — reduces the probabilistic failure surface. |
| 9 | First feature — Project Name + Business Outcome | Deliver the first usable MVP that turns one project idea into a validated name and outcome via CLI. | **End-to-end slice before breadth**: the vertical slice (CLI → LLM → schema → display) proves the whole chain works before expanding; the smallest useful product is shipped first. |
| 10 | Testing | Adopt pytest and write the first unit tests for schema validation. | **Test the deterministic parts**: validation rules are pure and cheap to test, so coverage starts where Python, not the LLM, is the source of guarantees. |
| 11 | LLM configuration | Externalize provider/model/temperature/max-tokens into `config/llm.yaml` with a loader. | **Config-as-data over config-in-code**: model/temperature live beside each other in YAML so behavior changes (e.g., switching models) don't require a redeploy or code change. |
| 12 | Configuration validation | Type the config as `LLMConfig` with field constraints so bad settings fail at load time. | **Fail-fast config**: invalid temperature/max-tokens surface at startup (typed `LLMConfig`), not as odd behavior at runtime — the same discipline as data validation, applied to settings. |
| 13 | Settings / environment config | Load secrets from `.env` into a Pydantic `Settings` object via `pydantic-settings`. | **Secrets separate from configuration**: non-sensitive settings in YAML, secrets in environment — different change cadence and exposure, enforced by two distinct models. |
| 14 | Application exceptions | Introduce `exceptions.py` with `ProjectGenerationError` and distinguish input errors from generation errors. | **Semantic error hierarchy**: input errors (`ValueError`) and generation failures (`ProjectGenerationError`) are distinct so callers can react appropriately; **chained raising** (`from exc`) preserves the root cause for debugging. |
| 15 | Logging | Add `configure_logging()` with a structured INFO format and `request_id` traces across stages. | **Correlation via request_id**: a single ID threads through every log line so a whole generation is reconstructible — foundation for future tracing and observability. |
| 16 | Telemetry | Record `GenerationTelemetry` (latency, optional token use) around each generation call. | **Measure what you optimize**: latency is captured with `perf_counter` around the LLM call; token counts stay `None` unless the provider reports them — honest data rather than invented metrics. |
| 17 | Generation result | Bundle blueprint + telemetry into a single `GenerationResult` returned by the generator. | **Result object pattern**: blueprint (data) + telemetry (metadata) travel together as one return contract — callers can't forget one half, and the shape survives interface changes. |
| 18 | Application service | Extract the use case into `ProjectBlueprintService`, separating CLI concerns from LLM interaction. | **Use-case layer**: the CLI (presentation) and the LLM (infrastructure) are decoupled by a service that owns *what the app does*; dependencies are injected via constructor so the use case is testable with a fake. |
| 19 | Generator interface | Define `ProjectGeneratorInterface` (ABC) and make the service depend on the abstraction, not the implementation. | **Dependency inversion**: the service depends on a contract, so OpenRouter, a fake, or a future provider are interchangeable — enables testing without any LLM call and provider switching without touching core logic. |
| 20 | Composition root | Move object construction into `create_application()` so the whole object graph is assembled in one place. | **Single construction point**: wiring (generator → service → application) happens in exactly one place; changing a dependency (e.g., injecting a fake) is a one-line change, and construction never leaks into modules. |
| 21 | PromptManager | Extract prompt management into a dedicated `PromptManager` with versioning stored in `config/prompts.yaml` and the version recorded in telemetry. | **Prompt as a first-class, versioned asset**: generation logic stops importing prompt strings directly; the version travels in telemetry so output quality can be traced back to the exact prompt that produced it. |
| 22 | File-based versioned prompts | Store prompt templates on disk under `prompts/<name>/<version>/` so `config/prompts.yaml` selects the active version without code changes. | **Config selects the version**: the filename layout (`<name>/<version>/`) enables prompt evolution and rollback by flipping config, not redeploying — prerequisites for prompt regression testing. |
| 23 | Typed request/response models | Validate input at the boundary and return typed responses so the same use case can serve CLI, API, or UI. | **Boundary contracts**: `GenerateBlueprintRequest`/`Response` make the application's interface explicit and validated, so the same use case is reachable from a CLI, FastAPI, or Streamlit without core changes — the first step toward a service/API layer. |

Legend: completed steps 1–23.

## Architecture after Step 20

```text
app.py (CLI)
   → Application (application.py, composition root)
      → ProjectBlueprintService (service.py)
         → ProjectGeneratorInterface (interfaces.py, ABC)
            → ProjectGenerator (generator.py)
               ├── PromptManager (prompt_manager.py) → prompts/<name>/<version>/*.txt
               └── ChatOpenAI (LangChain) → OpenRouter
```

**13 tests passing** (`tests/test_schemas.py`, `test_config.py`, `test_settings.py`, `test_service.py`, `test_application.py`, `test_prompt_manager.py`).