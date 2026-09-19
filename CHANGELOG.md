# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version History

| Version | Feature Domain | Key Objectives |
| --- | --- | --- |
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