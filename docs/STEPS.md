# Blueprint-Generator — STEPS

Progressive learning steps for the `blueprint-generator` project (idea → structured blueprint).
Each row records a completed increment with its one-sentence summary and the concepts it teaches.

| Step | Name | Summary | Key Concepts |
| --- | --- | --- | --- |
| 1 | Project foundation | Initialize the `blueprint-generator` project with `uv`, a virtual environment, dependencies, `.env`/`.env.example`, `.gitignore`, and Git. | `uv`, `pyproject.toml`, virtual environments, dependency management, environment variables, `.gitignore`, `git init` |
| 2 | Initial application structure | Scaffold the minimal module layout (`app.py`, `generator.py`, `schemas.py`, `prompts.py`) so each future concern has a home. | Project structure, separation of concerns, import graph, CLI entrypoint |
| 3 | Pydantic Blueprint schema | Define the first structured output model `ProjectBlueprint` with `project_name` and `business_outcome`. | Pydantic, `BaseModel`, type safety, structured data, schema-as-contract |
| 4 | Schema field validation | Add field descriptions and `field_validator` rules that strip whitespace and reject empty values. | `Field(...)`, `field_validator`, validation vs typing, fail-fast on malformed data |
| 5 | OpenRouter connection | Set up the `ProjectGenerator` to send a project idea to OpenRouter via the OpenAI SDK. | LLM APIs, HTTP-based model access, API keys, model + temperature + token params |
| 6 | Prompt engineering v1 | Build `SYSTEM_PROMPT` and `build_user_prompt()` that frame the LLM's role and task. | System vs user prompts, prompt framing, instruction clarity, determinism through prompting |
| 7 | LangChain OpenRouter client | Move to LangChain's `ChatOpenAI` with message tuples and a `SecretStr` API key for OpenRouter. | LangChain, `ChatOpenAI`, chat message format, secret handling with `SecretStr` |
| 8 | Structured LLM output | Use `with_structured_output(ProjectBlueprint)` so the LLM returns a typed Pydantic object. | LangChain structured output, schema binding to LLM, reducing manual parsing |
| 9 | First feature — Project Name + Business Outcome | Deliver the first usable MVP that turns one project idea into a validated name and outcome via CLI. | End-to-end feature, idea → LLM → Pydantic → display, minimal viable milestone |
| 10 | Testing | Adopt pytest and write the first unit tests for schema validation. | pytest, unit tests, test cases for validation rules, assert-driven verification |
| 11 | LLM configuration | Externalize provider/model/temperature/max-tokens into `config/llm.yaml` with a loader. | Config-as-data, YAML, `load_llm_config`, separating config from code |
| 12 | Configuration validation | Type the config as `LLMConfig` with field constraints so bad settings fail at load time. | Typed config, value constraints, fail-fast configuration, `test_config` |
| 13 | Settings / environment config | Load secrets from `.env` into a Pydantic `Settings` object via `pydantic-settings`. | `pydantic-settings`, `.env` handling, secrets vs config separation, `test_settings` |
| 14 | Application exceptions | Introduce `exceptions.py` with `ProjectGenerationError` and distinguish input errors from generation errors. | Exception hierarchy, chained raising (`from exc`), context preservation |
| 15 | Logging | Add `configure_logging()` with a structured INFO format and `request_id` traces across stages. | Logging configuration, structured logs, request correlation IDs, debuggability |
| 16 | Telemetry | Record `GenerationTelemetry` (latency, optional token use) around each generation call. | Observability, latency timing, honest optional token fields, perf measurement |
| 17 | Generation result | Bundle blueprint + telemetry into a single `GenerationResult` returned by the generator. | Result object pattern, data + metadata cohesion, single return contract |
| 18 | Application service | Extract the use case into `ProjectBlueprintService`, separating CLI concerns from LLM interaction. | Layering, use-case/service layer, dependency injection (constructor), testable boundary |
| 19 | Generator interface | Define `ProjectGeneratorInterface` (ABC) and make the service depend on the abstraction, not the implementation. | Dependence inversion, `ABC`/`abstractmethod`, contract-first design, swap providers/fakes |
| 20 | Composition root | Move object construction into `create_application()` so the whole object graph is assembled in one place. | Composition root, `Application` facade, dependency assembly, single construct point |
| 21 | PromptManager | Extract prompt management into a dedicated `PromptManager` with versioning stored in `config/prompts.yaml` and the version recorded in telemetry. | Prompt as managed asset, prompt versioning, config-driven version, separation from generation logic |
| 22 | File-based versioned prompts | Store prompt templates on disk under `prompts/<name>/<version>/` so `config/prompts.yaml` selects the active version without code changes. | Prompt files, template placeholders, config-as-selector, version switching without redeploys |

Legend: completed steps 1–22.

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

**12 tests passing** (`tests/test_schemas.py`, `test_config.py`, `test_settings.py`, `test_service.py`, `test_application.py`, `test_prompt_manager.py`).