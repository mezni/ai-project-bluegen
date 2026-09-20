# Session Handoff

Date: 2026-09-20

## Project State

An agentic AI learning project that transforms a simple AI project idea into a structured, implementation-ready architecture blueprint. Built progressively with Python, Pydantic, LangChain, and OpenRouter.

Current stage: **Level 1 — Structured LLM** functional end-to-end, behind a clean layered architecture with fully injected dependencies, a container-based composition root, request context, and structured logging:

```text
app.py (launcher)
   → CLI (cli.py — replaceable presentation layer)
      → Application (application.py — creates RequestContext at the use-case boundary)
         → ProjectBlueprintService (service.py)
            → ProjectGeneratorInterface (interfaces.py, ABC)
               → ProjectGenerator (generator.py)
                  ├── PromptManagerInterface (interfaces.py, ABC)
                  │   ├── PromptManager (prompt_manager.py) → prompts/<name>/<version>/*.txt
                  │   └── FakePromptManager (tests/fakes.py)
                  └── StructuredLLMInterface (interfaces.py, ABC)
                      ├── LangChainStructuredLLM (structured_llm.py) → ChatOpenAI → OpenRouter
                      └── FakeLLM (tests/fakes.py)
   object graph assembled by DependencyContainer (container.py) via create_application (application.py)
```

Key properties:

* The application flow depends only on typed contracts (`GenerateBlueprintRequest`/`GenerateBlueprintResponse`).
* `config.py` is the single configuration boundary — `Settings` (from `.env`) + `LLMConfig` (from `config/llm.yaml`).
* `DependencyContainer` knows how to construct infrastructure only; it never executes use cases. The composition root (`create_application`) accepts an injected generator and/or container for tests.
* `RequestContext` is frozen and created at the application boundary; its `request_id` threads through service → generator → telemetry → logs.
* Every log line carries `request_id` and `operation` fields via `StructuredLogger` + `RequestContextFilter`; ordinary logs that omit the fields still render.
* The generator is fully testable with `FakeLLM` + `FakePromptManager`; no filesystem or OpenRouter access is needed to exercise the real generate flow.
* Structured output is owned by the `LangChainStructuredLLM` adapter, not spread through the generator.
* Prompts are versioned files on disk; `config/prompts.yaml` selects the active version; the version is recorded in telemetry.

## Completed

| Release | Feature Domain | What was built |
| --- | --- | --- |
| 0.0.1 | Project foundation | Python env, `uv` project, dependencies, `.env`, Git |
| 0.0.2 | Initial project structure | `app.py`, `generator.py`, `schemas.py`, `prompts.py`, `.env.example` |
| 0.0.3 | Pydantic Blueprint schema | `ProjectBlueprint` (`project_name`, `business_outcome`) |
| 0.0.4 | Schema field validation | `Field` descriptions + `field_validator` (strip, reject empty) |
| 0.0.5 | OpenRouter LLM client | `ProjectGenerator` via `openai` SDK |
| 0.0.6 | Prompt engineering | `SYSTEM_PROMPT` + `build_user_prompt` |
| 0.0.7 | LangChain OpenRouter client | `ChatOpenAI`, message tuples, `SecretStr` API key |
| 0.0.8 | Structured LLM output | `with_structured_output(ProjectBlueprint)`; CLI prints typed fields |
| 0.0.9 | Testing | `tests/test_schemas.py` (3 tests), pytest config |
| 0.0.10 | Configuration | `config/llm.yaml`, `load_llm_config` |
| 0.0.11 | Configuration validation | Typed `LLMConfig`, field constraints, `tests/test_config.py` |
| 0.0.12 | Settings / env config | `pydantic-settings` `Settings`, `.env` loading, `tests/test_settings.py` |
| 0.0.13 | Application exceptions | `exceptions.py` (`ProjectGenerationError`), chained wrapping |
| 0.0.14 | Logging | `logging_config.py` structured format, `request_id` traces |
| 0.0.15 | Telemetry | `telemetry.py` `GenerationTelemetry` (latency, honest optional token fields) |
| 0.0.16 | Generation result | `GenerationResult` (blueprint + telemetry) |
| 0.0.17 | Service layer | `ProjectBlueprintService`, dependency injection, fake-generator test |
| 0.0.18 | Interfaces / dependency inversion | `interfaces.py` ABC, service depends on abstraction |
| 0.0.19 | Application layer | `Application` + `create_application(generator=None)` composition root |
| 0.0.20 | Prompt management | `PromptManager` abstraction, prompt versioning, versioned telemetry |
| 0.0.21 | File-based versioned prompts | `prompts/project_blueprint/v1/`, config selects active version |
| 0.0.22 | Typed request/response models | `GenerateBlueprintRequest`/`Response`, boundary validation |
| 0.0.23 | CLI separation | Dedicated `CLI`, `app.py` reduced to a launcher |
| 0.0.24 | LLM dependency injection | `LLMInterface`, injectable LLM, fake-based generator test |
| 0.0.25 | Structured LLM abstraction | `StructuredLLMInterface`, `LangChainStructuredLLM` adapter, no conditional branches |
| 0.0.26 | Configuration boundary / composition root | LLM adapter receives `config` + `settings` via constructor; generator requires injected LLM |
| 0.0.27 | Full dependency injection | `ProjectGenerator` requires injected LLM + prompt manager; tests need no filesystem |
| 0.0.28 | Prompt manager interface | `PromptManagerInterface`; generator depends on abstraction; `FakePromptManager` implements it |
| 0.0.29 | Request context | Frozen `RequestContext` created at the application boundary; `request_id` flows through the pipeline |
| 0.0.30 | Structured logging | `StructuredLogger` + `RequestContextFilter`; `request_id`/`operation` on every log line |

Test status: **16 passed**.

## Current Structure

```text
ai-project-bluegen/
│
├── app.py                  # Launcher: from cli import main
├── cli.py                  # CLI: configure_logging, args → request → application → formatted output (replaceable)
├── application.py          # Application + create_application (composition root, creates RequestContext)
├── container.py            # DependencyContainer: creates prompt manager / structured LLM / generator / service
├── context.py              # RequestContext (frozen request_id + create())
├── service.py              # ProjectBlueprintService (forwards context to generator)
├── interfaces.py           # ProjectGeneratorInterface + StructuredLLMInterface + PromptManagerInterface (ABCs)
├── generator.py            # ProjectGenerator: still injectable, structured logging via StructuredLogger
├── structured_llm.py       # LangChainStructuredLLM: ChatOpenAI + with_structured_output (config+settings injected)
├── prompt_manager.py       # PromptManager: loads versioned prompt files (implements PromptManagerInterface)
├── logger.py               # StructuredLogger: info/error/exception with request_id/operation extras
├── schemas.py              # ProjectBlueprint, GenerateBlueprintRequest/Response, GenerationTelemetryResponse
├── exceptions.py           # ProjectGenerationError
├── telemetry.py            # GenerationTelemetry, GenerationResult (dataclasses)
├── logging_config.py       # RequestContextFilter + configure_logging() (StreamHandler, clears handlers)
├── config.py               # Settings (env) + LLMConfig (yaml) — the configuration boundary
├── config/
│   ├── llm.yaml            # provider, base_url, model, temperature, max_tokens
│   └── prompts.yaml        # project_blueprint: version + path
├── prompts/
│   └── project_blueprint/
│       └── v1/
│           ├── system.txt  # system prompt template
│           └── user.txt    # user prompt template ({project_idea})
├── tests/
│   ├── fakes.py            # FakeLLM, FakePromptManager (interface impls), FakeProjectGenerator (no network/filesystem)
│   ├── test_schemas.py     # request/response schema tests
│   ├── test_config.py      # LLMConfig validation
│   ├── test_settings.py    # Settings/.env
│   ├── test_prompt_manager.py
│   ├── test_context.py     # RequestContext creation + immutability
│   ├── test_service.py     # fake generator
│   ├── test_application.py # fake generator + injected container through create_application
│   └── test_generator.py   # fake LLM + fake prompt manager through the real generator
├── .env                    # OPENROUTER_API_KEY (set), OPENROUTER_MODEL
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
├── CHANGELOG.md            # 0.0.1–0.0.30 (newest first)
├── README.md               # Full 21-section project document
├── docs/
│   ├── ROADMAP.md          # 42-step roadmap with status markers
│   ├── STEPS.md            # granular learning steps 1–31 with "choices + why"
│   └── SESSION_HANDOFF.md  # this file
└── .venv/
```

## Key Decisions

* Start simple; add complexity only when it solves a real problem.
* Use AI for ambiguity and reasoning; use deterministic Python for rules and guarantees.
* Each increment of work = next `0.0.x` release; entries added to `CHANGELOG.md` only as work completes.
* Building convention: `concept → implementation → failure modes` at each step.
* Not jumping directly to a multi-agent system; evolving Level 1 → pipeline → agentic.
* Depend on abstractions (`ProjectGeneratorInterface`, `StructuredLLMInterface`, `PromptManagerInterface`), inject at the composition root.
* `config.py` is the single configuration boundary — settings (`Settings`) and LLM config (`LLMConfig`) are loaded there and injected, never fetched at point of use.
* `DependencyContainer` constructs infrastructure (`PromptManager`, `LangChainStructuredLLM`, `ProjectGenerator`, `ProjectBlueprintService`); it never runs the use case. Tests can inject a container to avoid touching `.env`/`config/llm.yaml`.
* Structured output is an adapter concern (`LangChainStructuredLLM`) — the generator is provider-agnostic.
* Prompts are versioned files (`prompts/<name>/<version>/`); `config/prompts.yaml` selects the active version; the version is recorded in telemetry.
* The interaction surface (`CLI`) is replaceable: the application speaks typed request/response contracts.
* LLM config lives in `config/llm.yaml` (typed `LLMConfig`); secrets live in `.env` (typed `Settings`).
* `RequestContext` is a frozen dataclass created at the application boundary; the `request_id` it owns is the one used everywhere (service → generator → telemetry → logs).
* All application logging goes through `StructuredLogger` with `request_id`/`operation` extras; `RequestContextFilter` keeps non-application logs from crashing the formatter.
* **Never invent token counts** — token fields stay `None` unless the provider reports usage.
* Free model in use: `nvidia/nemotron-3-ultra-550b-a55b:free` (confirmed structured output). Fallback candidate: `openai/gpt-4o-mini`.

## Dependencies

```text
langchain>=1.4.2          langchain-openai>=1.6.2    langchain-openrouter>=0.2.8
openai>=3.16.2            pydantic>=2.12.5           pydantic-settings
python-dotenv>=1.2.3      pyyaml
dev: pytest>=9.1.1
```

Python `>=3.12`.

## Commands

```text
uv run python app.py "Build an AI system that classifies corporate documents."
uv run pytest        # 16 passed
```

## Next Steps — From STEPS.md (Roadmap Step 7: Complete Single-Agent Blueprint)

The goal is to expand `ProjectBlueprint` beyond name + business outcome to a complete single-agent blueprint.

Planned fields (from the blueprint reasoning list):

```text
requirements
boundaries
constraints
agents
orchestration
context
state
memory
knowledge
actions
authority
runtime
recovery
evaluation
observability
security
```

Objectives:

* Nested Pydantic models (per-section schemas)
* List fields with validation
* Update prompt v2 (`prompts/project_blueprint/v2/`) to generate the full blueprint
* Extend tests

## Immediate Follow-ups

1. Expand `schemas.py` toward the full blueprint (Roadmap Step 7) → next release 0.0.31.
2. Add `CHANGELOG.md` rows/entries as each version completes (current latest: 0.0.30).
3. Keep `docs/STEPS.md` and `docs/ROADMAP.md` status markers current (Roadmap Step 23 Observability completed ✅; broader traces/metrics/token usage belong to Phase 39 Production telemetry).
4. Do not create agents/, tools/, api/ directories yet — they come later per plan.

## Todo

- [ ] Roadmap Step 7 — Complete single-agent blueprint (`schemas.py` expansion + prompt v2)
- [ ] Step 8 — Prompt engineering v2 (`prompts/<name>/v2` with few-shot examples)
- [ ] Step 9 — Validation layer (deterministic Python validation)
- [ ] Integration tests for the real LLM path (free model)
- [ ] Observability follow-ups — token usage capture from the provider, traces, metrics (Roadmap Phase 39)
- [ ] Roadmap Step 11+ — per `docs/ROADMAP.md`