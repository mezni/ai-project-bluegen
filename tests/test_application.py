from application import Application, create_application
from config import LLMConfig, Settings
from container import DependencyContainer
from interfaces import ProjectGeneratorInterface
from schemas import (
    GenerateBlueprintRequest,
    ProjectBlueprint,
)
from service import ProjectBlueprintService
from telemetry import (
    GenerationResult,
    GenerationTelemetry,
)
from telemetry_recorder import InMemoryTelemetryRecorder
from tests.fakes import FakeProjectGenerator
from tracing import TraceContext


class CapturingGenerator(ProjectGeneratorInterface):

    def __init__(self) -> None:
        self.trace: TraceContext | None = None

    def generate(
        self,
        project_idea: str,
        trace: TraceContext,
    ) -> GenerationResult:

        self.trace = trace

        return GenerationResult(
            blueprint=ProjectBlueprint(
                project_name="Test Project",
                business_outcome="Test outcome.",
            ),
            telemetry=GenerationTelemetry(
                request_id=trace.context.request_id,
                model="fake-model",
                prompt_version="test-v1",
                latency_seconds=0.01,
            ),
        )


def test_create_application_with_custom_generator() -> None:
    container = DependencyContainer(
        settings=Settings(
            openrouter_api_key="test-key",
        ),
        llm_config=LLMConfig(
            provider="openrouter",
            base_url="https://openrouter.ai/api/v1",
            model="openai/gpt-4o-mini",
            temperature=0.2,
            max_tokens=1000,
        ),
    )

    application = create_application(
        generator=FakeProjectGenerator(),
        container=container,
    )

    request = GenerateBlueprintRequest(
        project_idea="Build an AI document classifier."
    )

    result = application.generate_blueprint(request)

    assert result.blueprint.project_name == "Test Project"
    assert result.telemetry.request_id
    assert len(result.telemetry.request_id) == 36
    assert result.telemetry.model == "fake-model"
    assert result.telemetry.prompt_version == "test-v1"


def test_application_creates_trace_context() -> None:
    generator = CapturingGenerator()

    service = ProjectBlueprintService(generator)

    recorder = InMemoryTelemetryRecorder()

    application = Application(
        blueprint_service=service,
        telemetry_recorder=recorder,
    )

    request = GenerateBlueprintRequest(
        project_idea="Build an AI document classifier."
    )

    response = application.generate_blueprint(request)

    assert generator.trace is not None
    assert (
        generator.trace.context.request_id
        == response.telemetry.request_id
    )
    assert generator.trace.recorder is recorder
    assert generator.trace.current_span_id is None
