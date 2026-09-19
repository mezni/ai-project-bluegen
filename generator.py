import logging
import time
import uuid

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from config import load_llm_config, load_settings
from exceptions import ProjectGenerationError
from interfaces import LLMInterface, ProjectGeneratorInterface
from prompt_manager import PromptManager
from schemas import ProjectBlueprint
from telemetry import GenerationResult, GenerationTelemetry


logger = logging.getLogger(__name__)

load_dotenv()


class ProjectGenerator(ProjectGeneratorInterface):
    def __init__(
        self,
        llm: LLMInterface | None = None,
        prompt_manager: PromptManager | None = None,
    ) -> None:

        settings = load_settings()
        config = load_llm_config()

        self.llm = llm or ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            base_url=config.base_url,
            api_key=settings.openrouter_api_key,
        )

        self.prompt_manager = (
            prompt_manager or PromptManager()
        )

        self.structured_llm = (
            self.llm.with_structured_output(ProjectBlueprint)
            if llm is None
            else llm
        )

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
                "Calling LLM | request_id=%s",
                request_id,
            )

            blueprint = self.structured_llm.invoke(messages)

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