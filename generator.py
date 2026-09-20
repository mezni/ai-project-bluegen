import logging
import time
import uuid

from exceptions import ProjectGenerationError
from interfaces import (
    ProjectGeneratorInterface,
    PromptManagerInterface,
    StructuredLLMInterface,
)
from telemetry import (
    GenerationResult,
    GenerationTelemetry,
)


logger = logging.getLogger(__name__)


class ProjectGenerator(ProjectGeneratorInterface):

    def __init__(
        self,
        llm: StructuredLLMInterface,
        prompt_manager: PromptManagerInterface,
    ) -> None:

        self.llm = llm
        self.prompt_manager = prompt_manager

    def generate(
        self,
        project_idea: str,
    ) -> GenerationResult:

        project_idea = project_idea.strip()

        if not project_idea:
            raise ValueError(
                "Project idea cannot be empty."
            )

        request_id = str(uuid.uuid4())

        logger.info(
            "Starting blueprint generation | request_id=%s",
            request_id,
        )

        messages = [
            (
                "system",
                self.prompt_manager.get_system_prompt(),
            ),
            (
                "human",
                self.prompt_manager.build_user_prompt(
                    project_idea
                ),
            ),
        ]

        start_time = time.perf_counter()

        try:
            logger.info(
                "Calling structured LLM | request_id=%s",
                request_id,
            )

            blueprint = self.llm.generate(messages)

            latency = time.perf_counter() - start_time

            logger.info(
                "Blueprint generation completed | request_id=%s",
                request_id,
            )

        except Exception as exc:
            latency = time.perf_counter() - start_time

            logger.exception(
                "Blueprint generation failed | request_id=%s",
                request_id,
            )

            raise ProjectGenerationError(
                "Failed to generate the project blueprint."
            ) from exc

        telemetry = GenerationTelemetry(
            request_id=request_id,
            model=self.llm.model_name,
            prompt_version=self.prompt_manager.get_version(),
            latency_seconds=latency,
        )

        return GenerationResult(
            blueprint=blueprint,
            telemetry=telemetry,
        )