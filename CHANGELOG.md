# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adopts [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Version History

| Version | Feature Domain | Key Objectives |
| --- | --- | --- |
| 0.0.1 | Project foundation | Python project structure, uv, virtual environments, .env, Git |
| 0.0.2 | Pydantic Blueprint schema | Pydantic, type safety, validation, structured data |
| 0.0.3 | OpenRouter LLM client | LLM APIs, models, temperature, tokens, configuration |
| 0.0.4 | First simple prompt | Prompt engineering, system vs user prompts |
| 0.0.5 | Structured LLM output | LangChain structured output + Pydantic |
| 0.0.6 | Project Name + Business Outcome | Your first real feature; extracting useful structured information from an idea |
| 0.0.7 | Complete single-agent blueprint | Generate boundaries, constraints, agents, knowledge, actions, etc. |
| 0.0.8 | Prompt engineering v2 | Better instructions, constraints, few-shot examples, output quality |
| 0.0.9 | Validation layer | Pydantic validation + deterministic Python validation |
| 0.0.10 | Tests | Unit tests, integration tests, test cases for LLM applications |
| 0.0.11 | LCEL pipeline | LangChain Expression Language, chains, composition |
| 0.0.12 | Multi-stage pipeline | Requirements → Architecture → Security → Critic → Blueprint |
| 0.0.13 | Shared state | TypedDict, workflow state, passing results between stages |
| 0.0.14 | Critic/revision loop | AI evaluation, iterative generation, revision |
| 0.0.15 | First real agentic version | Agent vs chain vs pipeline; when an LLM should make decisions |
| 0.0.16 | Specialized agents | Requirements Agent, Architecture Agent, Security Agent, Critic Agent |
| 0.0.17 | Orchestrator | Routing, delegation, agent coordination |
| 0.0.18 | Tool calling | Function/tool schemas, tool selection, controlled actions |
| 0.0.19 | Deterministic tools | Validators, cost calculator, architecture checker |
| 0.0.20 | Authority boundaries | Permissions, least privilege, allowed/forbidden actions |
| 0.0.21 | Human-in-the-loop | Approval gates, high-risk actions, escalation |
| 0.0.22 | Recovery | Retry, fallback model, invalid output recovery, failure handling |
| 0.0.23 | Observability | Logs, request IDs, traces, latency, token usage, errors |
| 0.0.24 | Evaluation | Accuracy, completeness, relevance, hallucination, structured evals |
| 0.0.25 | Evaluation dataset | Golden examples, expected outputs, regression testing |
| 0.0.26 | Knowledge/RAG | Documents → chunks → embeddings → vector store → retrieval |
| 0.0.27 | Architecture knowledge base | Security policies, architecture standards, reference architectures |
| 0.0.28 | Retrieval tools | Agents querying authoritative knowledge |
| 0.0.29 | Context engineering | What information each agent receives and why |
| 0.0.30 | State vs memory vs knowledge | Workflow state, persistent memory, external knowledge |
| 0.0.31 | Memory | User/project preferences and cross-interaction persistence |
| 0.0.32 | Security | Prompt injection, sensitive data, access control, data leakage |
| 0.0.33 | Responsible AI | Risk identification, human oversight, auditability |
| 0.0.34 | Production API | FastAPI, request/response models, service architecture |
| 0.0.35 | UI | Streamlit interface for the blueprint generator |
| 0.0.36 | Configuration | YAML/config management, dev/test/prod settings |
| 0.0.37 | CI/CD | GitHub Actions, tests, linting, deployment pipeline |
| 0.0.38 | Containerization | Docker, environment configuration |
| 0.0.39 | Production telemetry | Tracing, metrics, dashboards, LLM monitoring |
| 0.0.40 | Cost / FinOps | Token usage, model cost, cost per blueprint, optimization |
| 0.0.41 | Production evaluation | Automated quality gates before accepting a blueprint |
| 0.0.42 | Final production architecture | Put everything together into a production-grade agentic system |

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
* Initial Git repository