# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version History

| Version | Feature Domain | Key Objectives |
| --- | --- | --- |
| 0.0.29 | Request context | Immutable RequestContext created at the application boundary, request_id flows through the full pipeline |
| 0.0.28 | Prompt manager interface | PromptManagerInterface contract, generator depends on the abstraction, fake implements the interface |
| 0.0.27 | Full dependency injection | Generator requires injected LLM + prompt manager, fakes isolate tests from the filesystem and model calls |
| 0.0.26 | Configuration boundary / composition root | Config stays the only source of settings, dependencies injected into the LLM adapter, composition root assembles the graph |
| 0.0.25 | Structured LLM abstraction | Clean StructuredLLMInterface, structured output owned by the adapter, no conditional branches |
| 0.0.24 | LLM dependency injection | LLMInterface, injectable LLM, fully testable generator without real calls |
| 0.0.23 | CLI separation | Dedicated CLI class, app.py reduced to a launcher, replaceable interaction surface |
| 0.0.22 | Typed request/response models | Input validation schemas, typed API response for the application layer |
| 0.0.21 | File-based versioned prompts | Prompt templates on disk, config selects active version |
| 0.0.20 | Prompt management | Dedicated PromptManager, prompt versioning, versioned telemetry |
| 0.0.19 | Application layer | Composition root, app factory, no direct generator construction |
| 0.0.18 | Interfaces / dependency inversion | ABC, abstract method, service depends on interface |
| 0.0.17 | Service layer | Service abstraction, dependency injection, fake-generator tests |
| 0.0.16 | Generation result | Typed result wrapper, access to blueprint + telemetry |
| 0.0.15 | Telemetry | Latency measurement, telemetry model, honest token tracking |
| 0.0.14 | Logging | Structured log format, request_id tracing, log configuration |
| 0.0.13 | Application exceptions | Custom error, exception chaining, input vs generation errors |
| 0.0.12 | Settings / environment config | pydantic-settings, .env loading, Settings model, settings tests |
| 0.0.11 | Configuration validation | Typed LLMConfig, field constraints, config tests |
| 0.0.10 | Configuration | YAML config management, model settings, config-driven LLM client |
| 0.0.9 | Testing | pytest, unit tests, validation tests |
| 0.0.8 | Structured LLM output | LangChain structured output + Pydantic schema integration |
| 0.0.7 | LangChain OpenRouter client | ChatOpenAI, temperature, message tuples, LLM invoke |
| 0.0.6 | Prompt engineering | System vs user prompts, instructions, constraints, output requirements |
| 0.0.5 | OpenRouter LLM client | LLM APIs, API keys, models, direct client configuration |
| 0.0.4 | Schema field validation | Field descriptions, input stripping, empty value prevention |
| 0.0.3 | Pydantic Blueprint schema | Pydantic, type safety, validation, structured data |
| 0.0.2 | Initial project structure | Starter file skeleton: app, generator, schemas, prompts, env example |
| 0.0.1 | Project foundation | Python project structure, uv, virtual environments, .env, Git |

---

## [0.0.29] - 2026-09-20

### Request Context

**Feature Domain:** Request context

**Key Objectives:**

* Frozen `RequestContext` — the request ID cannot change during processing
* Context created at the application boundary (start of the use case)
* `request_id` flows through service, generator, and telemetry

### Added

* `context.py` — frozen `RequestContext` dataclass with `create()` factory generating a `uuid4` request ID
* `tests/test_context.py` — verifies a 36-character request ID is created and immutability raises `AttributeError`

### Changed

* `application.py` — `generate_blueprint` creates `RequestContext` and passes it to the service
* `service.py` — `generate_blueprint(project_idea, context)` forwards the context to the generator
* `interfaces.py` — `ProjectGeneratorInterface.generate` now accepts `context: RequestContext`
* `generator.py` — no longer crafts its own request ID (`uuid` import removed); logging and telemetry read `context.request_id`
* `tests/fakes.py` — `FakeProjectGenerator` implements the new signature and echoes `context.request_id`
* `tests/test_generator.py`, `tests/test_application.py`, `tests/test_service.py` — updated for the new signature and assertions

### Why

Request identity is now owned by the application boundary and immutable for the life of the request, so every downstream layer traces logs and telemetry under the exact same `request_id` without anyone re-deriving it.

---

## [0.0.28] - 2026-09-20

### Prompt Manager Interface

**Feature Domain:** Prompt manager interface

**Key Objectives:**

* Introduce a `PromptManagerInterface` contract
* Generator depends on the abstraction, not the concrete `PromptManager`
* Fakes explicitly implement the interface

### Added

* `interfaces.py` — `PromptManagerInterface` with `get_system_prompt()`, `build_user_prompt(project_idea)`, `get_version()`

### Changed

* `prompt_manager.py` — `PromptManager` now implements `PromptManagerInterface`
* `generator.py` — `ProjectGenerator` accepts `prompt_manager: PromptManagerInterface`; no import or dependency on the concrete `PromptManager`
* `application.py` — the composition root creates the concrete `PromptManager()` and injects it into the generator
* `tests/fakes.py` — `FakePromptManager` explicitly implements `PromptManagerInterface`

### Why

The generator is now coupled only to a prompt contract, so the concrete manager is an implementation detail owned by the composition root. Real and fake prompt managers are interchangeable, keeping every layer testable without touching the filesystem.

---

## [0.0.27] - 2026-09-20

### Full Dependency Injection

**Feature Domain:** Full dependency injection

**Key Objectives:**

* Generator requires both `llm` and `prompt_manager` at construction time
* No optional/defaulted dependencies — composition root supplies everything
* Unit tests isolated from both the filesystem and model calls via fakes

### Changed

* `generator.py` — `ProjectGenerator.__init__` now takes `llm: StructuredLLMInterface` and `prompt_manager: PromptManager` (both required); the optional `prompt_manager` default and internal `PromptManager()` construction are removed
* `application.py` — the composition root now passes `prompt_manager=PromptManager()` when assembling the generator
* `tests/fakes.py` — adds `FakePromptManager` (`get_system_prompt`, `build_user_prompt`, `get_version`)
* `tests/test_generator.py` — `test_generator_uses_injected_dependencies` injects `FakeLLM` + `FakePromptManager` and asserts telemetry `model == "fake-model"` and `prompt_version == "test-v1"`

### Why

The generator no longer constructs anything itself or touches the filesystem: prompts come from an injected `PromptManager` fake, and generation comes from an injected LLM fake. Tests exercise the full flow in isolation, and production wiring lives solely in the composition root.

---

## [0.0.26] - 2026-09-20

### Configuration Boundary and Composition Root

**Feature Domain:** Configuration boundary / composition root

**Key Objectives:**

* Keep `config.py` as the single configuration boundary (settings + YAML)
* Inject dependencies into the LLM adapter instead of self-loading them
* Make the composition root (`create_application`) the only place that assembles the graph

### Changed

* `structured_llm.py` — `LangChainStructuredLLM.__init__` now receives `config: LLMConfig` and `settings: Settings` instead of loading them itself
* `application.py` — `create_application` loads settings + LLM config, builds `LangChainStructuredLLM(config=..., settings=...)`, and wires the generator; it remains the composition root
* `generator.py` — `ProjectGenerator` requires an injected `StructuredLLMInterface`; the default `LangChainStructuredLLM()` fallback is removed since the adapter no longer has a no-arg constructor

### Why

Dependencies flow inward instead of being fetched at point of use: `config.py` remains the configuration boundary, adapters receive ready-to-use dependencies, and the only place connecting pieces together is `create_application`. Swapping providers or wiring order is now a single composition-root change, and every layer stays testable with fakes.

---

## [0.0.25] - 2026-09-19

### Structured LLM Abstraction

**Feature Domain:** Structured LLM abstraction

**Key Objectives:**

* Replace the temporary `llm is None` branch with a clean, structured-output contract
* Own the LangChain wiring inside a dedicated adapter
* Keep the generator portable across providers/fakes through the interface

### Added

* `structured_llm.py` — `LangChainStructuredLLM` builds `ChatOpenAI` + `with_structured_output(ProjectBlueprint)` and exposes `model_name`

### Changed

* `interfaces.py` — `StructuredLLMInterface` with `generate(messages) -> ProjectBlueprint` and a `model_name` property
* `generator.py` — injects a `StructuredLLMInterface` directly, no conditional construction branch; telemetry reads `self.llm.model_name`
* `tests/fakes.py` — `FakeLLM` implements the `model_name` property + `generate`
* `tests/test_generator.py` — asserts telemetry `model == "fake-model"` and `prompt_version == "v1"`

### Why

Structured output is a property of the adapter, not the generator. The temporary branching is gone, the contract is uniform, and swapping OpenRouter for another provider or a fake is a single constructor choice.

---

## [0.0.24] - 2026-09-19

### LLM Dependency Injection

**Feature Domain:** LLM dependency injection

**Key Objectives:**

* Introduce an `LLMInterface` contract for model invocation
* Let `ProjectGenerator` accept an injected LLM (real or fake)
* Make the generator fully testable without OpenRouter calls

### Added

* `interfaces.py` — `LLMInterface` ABC with `invoke()`
* `tests/fakes.py` — `FakeLLM` returning a validated `ProjectBlueprint` (never contacts OpenRouter)
* `tests/test_generator.py` — verifies `ProjectGenerator` uses an injected LLM and records `prompt_version`

### Changed

* `generator.py` — constructor takes `llm` and `prompt_manager`; builds `ChatOpenAI` + `with_structured_output` only when no LLM is injected

### Why

The generator no longer hard-depends on OpenRouter: tests exercise the full generate flow with a fake, and model/provider switching is now a constructor choice — the payoff of the interface established earlier.

---

## [0.0.23] - 2026-09-19

### CLI Separation

**Feature Domain:** CLI separation

**Key Objectives:**

* Move all presentation/CLI concerns into a dedicated `CLI`
* Reduce `app.py` to a thin launcher
* Make the interaction surface replaceable (CLI, API, UI) without touching the application flow

### Added

* `cli.py` — `CLI` (builds the request, calls the application, formats/prints the response) plus a `main()` that reads `sys.argv`

### Changed

* `app.py` — reduced to `from cli import main; main()`

### Why

The business/application flow no longer depends on how the user interacts with the system — a key lesson: swap `CLI` for FastAPI, Streamlit, or a queue consumer without changing the service or generator.

---

## [0.0.22] - 2026-09-19

### Typed Request/Response Models

**Feature Domain:** Typed request/response models

**Key Objectives:**

* Validate input at the application boundary via `GenerateBlueprintRequest`
* Return a typed `GenerateBlueprintResponse` from the application layer
* Prepare the application interface for API/Streamlit/Web use

### Added

* `schemas.py` — `GenerateBlueprintRequest` (validated, whitespace-stripped project idea), `GenerateBlueprintResponse`, `GenerationTelemetryResponse`

### Changed

* `application.py` — `generate_blueprint(request)` accepts a request model and maps service telemetry into `GenerationTelemetryResponse`
* `app.py` — builds a `GenerateBlueprintRequest` and prints from the typed response fields
* `tests/test_schemas.py` — request validation, whitespace stripping, empty-input rejection, response construction
* `tests/test_application.py` — passes a `GenerateBlueprintRequest` to the application

### Why

The application layer now speaks typed request/response contracts rather than raw strings, so the same use case can be served by a CLI, API, or UI without changing core logic.

---

## [0.0.21] - 2026-09-19

### File-Based Versioned Prompts

**Feature Domain:** File-based versioned prompts

**Key Objectives:**

* Prompt templates stored as files under `prompts/<name>/<version>/`
* `config/prompts.yaml` selects the active prompt version and base path
* Configuration (not code) determines which prompt version is used

### Added

* `prompts/project_blueprint/v1/system.txt` — system prompt template
* `prompts/project_blueprint/v1/user.txt` — user prompt template with `{project_idea}` placeholder

### Changed

* `prompt_manager.py` rewritten to resolve `base_path/version/{system,user}.txt` from `config/prompts.yaml`, with `get_version()`
* `config/prompts.yaml` now includes `path: "prompts/project_blueprint"` alongside `version`
* `generator.py` obtains `prompt_version` from `self.prompt_manager.get_version()`
* `tests/test_prompt_manager.py` adds a version assertion (`get_version() == "v1"`)

### Removed

* `prompts.py` — replaced by the file-based prompt store
* Unused `PromptsConfig` + `load_prompts_config()` from `config.py`

### Why

Prompts are now versioned assets on disk; changing `config/prompts.yaml` swaps the active version without code changes, preparing for prompt regression testing and rollback.

---

## [0.0.20] - 2026-09-19

### Prompt Management

**Feature Domain:** Prompt management

**Key Objectives:**

* Dedicated `PromptManager` abstraction for prompt building
* Versioned prompts via `config/prompts.yaml`
* `prompt_version` recorded in telemetry

### Added

* `prompt_manager.py` — `PromptManager` wrapping `SYSTEM_PROMPT` and `build_user_prompt`
* `config/prompts.yaml` — `project_blueprint.version: "v1"`
* `tests/test_prompt_manager.py` — verifies system prompt content and user prompt embedding

### Changed

* `generator.py` injects `PromptManager` (optional) and builds messages through it; reads `prompt_version` from `config/prompts.yaml`
* `config.py` adds `PromptsConfig` + `load_prompts_config()`
* `telemetry.py` — `GenerationTelemetry` gains a `prompt_version` field
* `tests/test_service.py` and `tests/test_application.py` fakes include `prompt_version`

### Why

Prompts are now managed as a versioned asset (config-driven) rather than imports scattered through the generator, preparing for prompt evolution and regression tracking.

---

## [0.0.19] - 2026-09-18

### Application Layer

**Feature Domain:** Application layer

**Key Objectives:**

* Composition root (`Application` + `create_application`)
* Optional generator injection
* App no longer constructs the generator directly

### Added

* `application.py` — `Application` wrapping a `ProjectBlueprintService`, plus `create_application(generator=None)` that builds the default generator or accepts an injected one
* `tests/test_application.py` — verifies `create_application` with a fake generator (no LLM call)

### Changed

* `app.py` uses `create_application()` and no longer imports/constructs `ProjectGenerator`

---

## [0.0.18] - 2026-09-18

### Interfaces / Dependency Inversion

**Feature Domain:** Interfaces / dependency inversion

**Key Objectives:**

* `abc.ABC` + `@abstractmethod`
* Service depends on an abstraction, not a concrete implementation

### Added

* `interfaces.py` — `ProjectGeneratorInterface` with abstract `generate(project_idea)`

### Changed

* `generator.py` — `ProjectGenerator` implements `ProjectGeneratorInterface`
* `service.py` — `ProjectBlueprintService` accepts `ProjectGeneratorInterface`
* `tests/test_service.py` — `FakeProjectGenerator` implements the interface

---

## [0.0.17] - 2026-09-18

### Service Layer

**Feature Domain:** Service layer

**Key Objectives:**

* Service abstraction over the generator
* Dependency injection
* Testability without calling OpenRouter

### Added

* `service.py` — `ProjectBlueprintService` wraps a generator and exposes `generate_blueprint(project_idea)`
* `tests/test_service.py` — uses a `FakeProjectGenerator` (no LLM call) to verify the service returns the blueprint + telemetry

### Changed

* `app.py` instantiates `ProjectBlueprintService(generator)` and calls `service.generate_blueprint(...)`

---

## [0.0.16] - 2026-09-18

### Generation Result

**Feature Domain:** Generation result

**Key Objectives:**

* Typed result wrapper around blueprint + telemetry
* CLI surfaces request ID and latency

### Changed

* `telemetry.py` adds `GenerationResult` (`blueprint` + `telemetry`)
* `generator.py` `generate()` now returns `GenerationResult` instead of a bare `ProjectBlueprint`
* `app.py` uses `result.blueprint` and prints `Request ID` and `Latency` from `result.telemetry`

---

## [0.0.15] - 2026-09-18

### Telemetry

**Feature Domain:** Telemetry

**Key Objectives:**

* Latency measurement with `time.perf_counter()`
* `GenerationTelemetry` dataclass
* Honest token tracking — never invent token counts

### Added

* `telemetry.py` — `GenerationTelemetry` with `request_id`, `model`, `latency_seconds`, and optional `input_tokens`/`output_tokens`/`total_tokens` (default `None`)

### Changed

* `generator.py` times the LLM call, logs LLM response metadata (temporary inspection), and logs generation telemetry (model + latency) on success

---

## [0.0.14] - 2026-09-18

### Logging

**Feature Domain:** Logging

**Key Objectives:**

* Structured log format (timestamp, level, logger, message)
* `request_id` tracing across generation stages
* Centralized logging configuration

### Added

* `logging_config.py` — `configure_logging()` sets INFO level with a structured format

### Changed

* `generator.py` logs start, LLM call, completion, warning (empty input), and exception (with traceback) — each tagged with a per-request `request_id` (uuid)
* `app.py` calls `configure_logging()` before running

---

## [0.0.13] - 2026-09-18

### Application Exceptions

**Feature Domain:** Application exceptions

**Key Objectives:**

* Custom application exception
* Exception chaining (`raise ... from exc`)
* Input vs generation error separation

### Added

* `exceptions.py` — `ProjectGenerationError`

### Changed

* `generator.py` wraps any `structured_llm.invoke` failure in `ProjectGenerationError` (preserving the original via `from exc`)
* `app.py` catches `ValueError` (input error) and `ProjectGenerationError` (generation error) separately, exiting with a clear message for each

---

## [0.0.12] - 2026-09-18

### Settings / Environment Configuration

**Feature Domain:** Settings / environment configuration

**Key Objectives:**

* `pydantic-settings` `BaseSettings`
* `.env` loading via `SettingsConfigDict`
* API key as typed setting

### Added

* `config.py` adds `Settings` (`openrouter_api_key` min length 1) and `load_settings()` — reads `.env` with `extra="ignore"`
* `tests/test_settings.py` with a test that reads `OPENROUTER_API_KEY` from the environment via `monkeypatch`

### Changed

* `generator.py` replaces `load_dotenv`/`os.getenv` with `Settings` — API key now comes from `settings.openrouter_api_key`
* `pyproject.toml` adds `pydantic-settings` as a dependency

---

## [0.0.11] - 2026-09-18

### Configuration Validation

**Feature Domain:** Configuration validation

**Key Objectives:**

* Typed `LLMConfig` model
* Field constraints (`temperature` 0.0–2.0, `max_tokens` > 0)
* Config validation tests

### Changed

* `config.py` `load_llm_config()` now returns a typed `LLMConfig` via `model_validate` instead of a raw dict
* `generator.py` uses attribute access (`config.model`, `config.temperature`, ...)

### Added

* `tests/test_config.py` with 3 tests — accepts valid config, rejects invalid temperature, rejects invalid max_tokens

---

## [0.0.10] - 2026-09-18

### Configuration

**Feature Domain:** Configuration

**Key Objectives:**

* YAML config management
* Model settings (model, temperature, max_tokens, base_url)
* Config-driven LLM client

### Added

* `config/llm.yaml` — YAML config with `provider`, `base_url`, `model`, `temperature`, `max_tokens`
* `config.py` — `load_llm_config()` reads the YAML config and raises `FileNotFoundError` / `ValueError` for missing or empty config

### Changed

* `pyproject.toml` adds `pyyaml` as a dependency
* `generator.py` builds `ChatOpenAI` from the YAML config values

---

## [0.0.9] - 2026-09-18

### Phase 8 — Testing

**Feature Domain:** Testing

**Key Objectives:**

* pytest
* Unit tests
* Validation tests

### Added

* `tests/test_schemas.py` with 3 tests — accepts valid blueprint data, rejects empty `project_name`, rejects empty `business_outcome`

### Changed

* `pyproject.toml` adds `pytest` as a dev dependency
* `pyproject.toml` adds `[tool.pytest.ini_options]` (`pythonpath = ["."]`, `testpaths = ["tests"]`) so `pytest` resolves the project root imports

---

## [0.0.8] - 2026-09-18

### Phase 5 — Structured LLM Output

**Feature Domain:** Structured LLM output

**Key Objectives:**

* LangChain structured output
* Pydantic integration
* Output parsing
* Validation failures

### Added

* `generator.py` builds a `structured_llm` via `self.llm.with_structured_output(ProjectBlueprint)`

### Changed

* `generator.py` `generate()` now invokes the structured LLM and returns a typed `ProjectBlueprint` (instead of raw text)
* `app.py` prints the typed result via `blueprint.project_name` and `blueprint.business_outcome`
* `schemas.py` tightens field descriptions: concise meaningful name, and business outcome focused on measurable value rather than technical implementation

---

## [0.0.7] - 2026-09-18

### LangChain OpenRouter Client

**Feature Domain:** LangChain OpenRouter client

**Key Objectives:**

* LangChain `ChatOpenAI`
* Model and temperature configuration
* System/human message tuples
* `llm.invoke`

### Changed

* `generator.py` replaces the `openai` SDK client with LangChain `ChatOpenAI` (model `nvidia/nemotron-3-ultra-550b-a55b:free`, `temperature=0.2`, OpenRouter `base_url`)
* `generator.py` sends `("system", ...)` / `("human", ...)` message tuples and returns `response.content` from `llm.invoke`
* `generator.py` reads the API key from `OPENROUTER_API_KEY` (falling back to `OPENAI_API_KEY`), raises `ValueError` if missing, and passes it as `SecretStr`

---

## [0.0.6] - 2026-09-18

### Phase 4 — Prompt Engineering

**Feature Domain:** Prompt engineering

**Key Objectives:**

* System vs user prompts
* Instructions
* Constraints
* Output requirements

### Added

* `prompts.py` adds `SYSTEM_PROMPT` — an AI architecture assistant that asks for a project name and business outcome while forbidding technical architecture design
* `prompts.py` adds `build_user_prompt(project_idea)` — wraps the project idea into a user prompt

### Changed

* `generator.py` now sends `SYSTEM_PROMPT` (system) and `build_user_prompt(project_idea)` (user) to the OpenRouter LLM

---

## [0.0.5] - 2026-09-18

### Phase 3 — OpenRouter LLM Client

**Feature Domain:** OpenRouter LLM client

**Key Objectives:**

* LLM APIs
* API keys
* Models
* Direct client configuration

### Added

* `generator.py` adds `ProjectGenerator` — an OpenRouter LLM client (via the `openai` SDK) that raises `ValueError` when `OPENROUTER_API_KEY` is not configured

### Changed

* `app.py` uses `ProjectGenerator` to generate a response for "Build an AI system that classifies corporate documents."

---

## [0.0.4] - 2026-09-18

### Schema Field Validation

**Feature Domain:** Schema field validation

**Key Objectives:**

* `Field` descriptions
* `field_validator`
* Input stripping
* Empty value prevention

### Changed

* `schemas.py` adds `Field` descriptions to `project_name` and `business_outcome`
* `schemas.py` adds a `field_validator` that strips whitespace and raises `ValueError` ("Value cannot be empty.") for empty values on both fields
* `app.py` verifies valid data still validates and dumps correctly

---

## [0.0.3] - 2026-09-18

### Phase 2 — Pydantic Blueprint Schema

**Feature Domain:** Pydantic Blueprint schema

**Key Objectives:**

* `BaseModel`
* Type hints and fields
* Validation
* Structured data

### Changed

* `schemas.py` now defines `ProjectBlueprint` with `project_name` and `business_outcome` fields (replaces the starter `ProjectIdea`/`Blueprint` placeholders)
* `app.py` tests the schema without an LLM — builds a `ProjectBlueprint`, prints it, and prints `model_dump()`

---

## [0.0.2] - 2026-09-18

### Initial Project Structure

**Feature Domain:** Initial project structure

**Key Objectives:**

* Deploy the starter file skeleton for the blueprint generator
* Define environment variable names for configuration

### Added

* `.env.example` with the documented variable names
* `app.py` minimal entry point (`main()` prints the generator name)
* `generator.py` placeholder `generate_blueprint(idea)`
* `schemas.py` starter Pydantic models (`ProjectIdea`, `Blueprint`)
* `prompts.py` initial system prompt

---

## [0.0.1] - 2026-09-18

### Phase 1 — Project Foundation

**Feature Domain:** Project foundation

**Key Objectives:**

* Python project structure
* `uv` project management
* Virtual environments
* `.env` configuration
* Git version control
* Dependencies

### Added

* `pyproject.toml` with project metadata and core dependencies (langchain, langchain-openrouter, pydantic, python-dotenv)
* `uv.lock` lockfile
* `.env` template for `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` configuration
* `.gitignore` for virtual environments, environment files, and Python caches
* `README.md` project documentation
* `docs/ROADMAP.md` learning roadmap
* `docs/SESSION_HANDOFF.md` session handoff document
* `CHANGELOG.md` changelog with version history
* Initial Git repository