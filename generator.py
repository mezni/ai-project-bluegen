import logging
import time
import uuid

from langchain_openai import ChatOpenAI

from config import load_llm_config, load_settings
from exceptions import ProjectGenerationError
from interfaces import ProjectGeneratorInterface
from prompts import SYSTEM_PROMPT, build_user_prompt
from schemas import ProjectBlueprint
from telemetry import GenerationResult, GenerationTelemetry


logger = logging.getLogger(__name__)


class ProjectGenerator(ProjectGeneratorInterface):
    def __init__(self) -> None:
        settings = load_settings()
        config = load_llm_config()

        self.llm = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            base_url=config.base_url,
            api_key=settings.openrouter_api_key,
        )

        self.structured_llm = self.llm.with_structured_output(
            ProjectBlueprint
        )

    def generate(self, project_idea: str) -> GenerationResult:
        request_id = str(uuid.uuid4())

        logger.info(
            "Starting project generation | request_id=%s",
            request_id,
        )

        project_idea = project_idea.strip()

        if not project_idea:
            logger.warning(
                "Empty project idea | request_id=%s",
                request_id,
            )
            raise ValueError("Project idea cannot be empty.")

        messages = [
            ("system", SYSTEM_PROMPT),
            ("human", build_user_prompt(project_idea)),
        ]

        start_time = time.perf_counter()

        try:
            logger.info(
                "Calling LLM | request_id=%s",
                request_id,
            )

            response = self.structured_llm.invoke(messages)

            latency = time.perf_counter() - start_time

            telemetry = GenerationTelemetry(
                request_id=request_id,
                model=self.llm.model_name,
                latency_seconds=latency,
            )

            logger.info(
                "Generation telemetry | request_id=%s | model=%s | latency=%.3fs",
                telemetry.request_id,
                telemetry.model,
                telemetry.latency_seconds,
            )

            logger.info(
                "Project generation completed | request_id=%s | latency=%.3fs",
                request_id,
                latency,
            )

            return GenerationResult(
                blueprint=response,
                telemetry=telemetry,
            )

        except Exception as exc:
            latency = time.perf_counter() - start_time

            logger.exception(
                "Project generation failed | request_id=%s | latency=%.3fs",
                request_id,
                latency,
            )

            raise ProjectGenerationError(
                "Failed to generate the project blueprint."
            ) from exc