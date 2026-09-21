import logging
import time

from context import RequestContext
from cost import CostCalculator, ModelPricing
from exceptions import ProjectGenerationError
from interfaces import (
    ProjectGeneratorInterface,
    PromptManagerInterface,
    StructuredLLMInterface,
    TelemetryRecorderInterface,
)
from logger import StructuredLogger
from telemetry import (
    GenerationEvent,
    GenerationResult,
    GenerationTelemetry,
)


class ProjectGenerator(ProjectGeneratorInterface):

    def __init__(
        self,
        llm: StructuredLLMInterface,
        prompt_manager: PromptManagerInterface,
        telemetry_recorder: TelemetryRecorderInterface,
        cost_calculator: CostCalculator,
        model_pricing: ModelPricing,
    ) -> None:

        self.llm = llm
        self.prompt_manager = prompt_manager
        self.telemetry_recorder = telemetry_recorder
        self.cost_calculator = cost_calculator
        self.model_pricing = model_pricing

        self.logger = StructuredLogger(
            logging.getLogger(__name__)
        )

    def generate(
        self,
        project_idea: str,
        context: RequestContext,
    ) -> GenerationResult:

        project_idea = project_idea.strip()

        if not project_idea:
            raise ValueError(
                "Project idea cannot be empty."
            )

        self.logger.info(
            "Starting blueprint generation",
            request_id=context.request_id,
            operation="generate_blueprint",
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
            self.logger.info(
                "Calling structured LLM",
                request_id=context.request_id,
                operation="llm_generation",
            )

            blueprint, usage = self.llm.generate(messages)

            latency = time.perf_counter() - start_time

            self.logger.info(
                "Blueprint generation completed",
                request_id=context.request_id,
                operation="generate_blueprint",
            )

        except Exception as exc:
            latency = time.perf_counter() - start_time

            self.logger.exception(
                "Blueprint generation failed",
                request_id=context.request_id,
                operation="generate_blueprint",
            )

            raise ProjectGenerationError(
                "Failed to generate the project blueprint."
            ) from exc

        telemetry = GenerationTelemetry(
            request_id=context.request_id,
            model=self.llm.model_name,
            prompt_version=self.prompt_manager.get_version(),
            latency_seconds=latency,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
        )

        cost = None

        if (
            usage.input_tokens is not None
            and usage.output_tokens is not None
        ):
            cost = self.cost_calculator.calculate(
                pricing=self.model_pricing,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
            )

        event = GenerationEvent(
            request_id=context.request_id,
            operation="project_blueprint_generation",
            model=self.llm.model_name,
            prompt_version=self.prompt_manager.get_version(),
            status="success",
            latency_seconds=latency,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            input_cost=(
                cost.input_cost
                if cost is not None
                else None
            ),
            output_cost=(
                cost.output_cost
                if cost is not None
                else None
            ),
            total_cost=(
                cost.total_cost
                if cost is not None
                else None
            ),
        )

        self.telemetry_recorder.record(event)

        return GenerationResult(
            blueprint=blueprint,
            telemetry=telemetry,
        )