from config import load_llm_config, load_settings
from container import DependencyContainer
from interfaces import ProjectGeneratorInterface
from schemas import (
    GenerateBlueprintRequest,
    GenerateBlueprintResponse,
    GenerationTelemetryResponse,
)
from service import ProjectBlueprintService


class Application:

    def __init__(
        self,
        blueprint_service: ProjectBlueprintService,
    ) -> None:

        self.blueprint_service = blueprint_service

    def generate_blueprint(
        self,
        request: GenerateBlueprintRequest,
    ) -> GenerateBlueprintResponse:

        result = (
            self.blueprint_service
            .generate_blueprint(
                request.project_idea
            )
        )

        telemetry = GenerationTelemetryResponse(
            request_id=result.telemetry.request_id,
            model=result.telemetry.model,
            prompt_version=result.telemetry.prompt_version,
            latency_seconds=result.telemetry.latency_seconds,
            input_tokens=result.telemetry.input_tokens,
            output_tokens=result.telemetry.output_tokens,
            total_tokens=result.telemetry.total_tokens,
        )

        return GenerateBlueprintResponse(
            blueprint=result.blueprint,
            telemetry=telemetry,
        )


def create_application(
    generator: ProjectGeneratorInterface | None = None,
    container: DependencyContainer | None = None,
) -> Application:

    if container is None:
        settings = load_settings()
        config = load_llm_config()

        container = DependencyContainer(
            settings=settings,
            llm_config=config,
        )

    if generator is None:

        prompt_manager = (
            container.create_prompt_manager()
        )

        llm = (
            container.create_structured_llm()
        )

        generator = container.create_generator(
            llm=llm,
            prompt_manager=prompt_manager,
        )

    service = container.create_service(
        generator
    )

    return Application(service)