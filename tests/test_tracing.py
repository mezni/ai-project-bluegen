import pytest

from context import RequestContext
from telemetry_recorder import InMemoryTelemetryRecorder
from tracing import Span, TraceContext


def test_span_records_success_event():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    span = Span.start(
        context=context,
        recorder=recorder,
        event_type="generation",
        operation="test_operation",
    )

    span.finish(
        status="success",
        model="fake-model",
    )

    assert len(recorder.events) == 1

    event = recorder.events[0]

    assert event.request_id == context.request_id
    assert event.trace_id == context.trace_id
    assert event.span_id
    assert event.event_type == "generation"
    assert event.operation == "test_operation"
    assert event.status == "success"
    assert event.model == "fake-model"
    assert event.latency_seconds >= 0


def test_span_records_parent_span():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    parent = Span.start(
        context=context,
        recorder=recorder,
        event_type="agent",
        operation="agent_execution",
    )

    child = Span.start(
        context=context,
        recorder=recorder,
        event_type="generation",
        operation="llm_generation",
        parent_span_id=parent.span_id,
    )

    child.finish(status="success")
    parent.finish(status="success")

    assert len(recorder.events) == 2

    child_event = recorder.events[0]
    parent_event = recorder.events[1]

    assert parent_event.parent_span_id is None
    assert child_event.parent_span_id == parent_event.span_id
    assert child_event.trace_id == parent_event.trace_id


def test_span_records_error_event():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    span = Span.start(
        context=context,
        recorder=recorder,
        event_type="generation",
        operation="test_operation",
    )

    span.finish(
        status="error",
        error_type="TimeoutError",
    )

    event = recorder.events[0]

    assert event.status == "error"
    assert event.error_type == "TimeoutError"
    assert event.latency_seconds >= 0


def test_trace_context_creates_parent_child_relationships():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    trace = TraceContext(
        context=context,
        recorder=recorder,
    )

    parent = trace.start_span(
        "agent",
        "agent_execution",
    )

    child = trace.start_span(
        "llm",
        "llm_generation",
    )

    assert parent.parent_span_id is None
    assert child.parent_span_id == parent.span_id

    assert trace.current_span_id == child.span_id


def test_trace_context_finishes_spans_in_lifo_order():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    trace = TraceContext(
        context=context,
        recorder=recorder,
    )

    parent = trace.start_span(
        "agent",
        "agent_execution",
    )

    child = trace.start_span(
        "llm",
        "llm_generation",
    )

    with pytest.raises(RuntimeError, match="LIFO"):
        trace.finish_span(
            parent,
            status="success",
        )

    trace.finish_span(
        child,
        status="success",
    )

    trace.finish_span(
        parent,
        status="success",
    )

    assert trace.current_span_id is None


def test_trace_context_records_nested_events():
    context = RequestContext.create()
    recorder = InMemoryTelemetryRecorder()

    trace = TraceContext(
        context=context,
        recorder=recorder,
    )

    parent = trace.start_span(
        "agent",
        "agent_execution",
    )

    child = trace.start_span(
        "llm",
        "llm_generation",
    )

    trace.finish_span(
        child,
        status="success",
    )

    trace.finish_span(
        parent,
        status="success",
    )

    assert len(recorder.events) == 2

    # Events are recorded in LIFO order (child first, then parent)
    child_event = recorder.events[0]
    parent_event = recorder.events[1]

    assert parent_event.trace_id == child_event.trace_id
    assert parent_event.span_id == child_event.parent_span_id