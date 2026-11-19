import pytest
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.response_helper import ResponseFactory
from ask_sdk_model import Intent, IntentRequest, LaunchRequest, RequestEnvelope, Response
from ask_sdk_model.interfaces.audioplayer import PlayDirective, StopDirective

from alexa_skill.lambda_function import (
    AudioPlayerEventHandler,
    CatchAllExceptionHandler,
    HelpIntentHandler,
    LaunchAndPlayHandler,
    StopAndCancelHandler,
)


def _build_handler_input(request):
    req_envelope = RequestEnvelope(request=request)
    return HandlerInput(request_envelope=req_envelope)


def test_launch_handler_can_handle_and_play():
    handler = LaunchAndPlayHandler()
    handler_input = _build_handler_input(LaunchRequest(request_id="r1", timestamp="2026-11-19T00:00:00Z"))

    assert handler.can_handle(handler_input)
    response = handler.handle(handler_input)

    assert isinstance(response, Response)
    assert response.should_end_session is True
    assert len(response.directives) == 1
    assert isinstance(response.directives[0], PlayDirective)
    assert response.directives[0].audio_item.stream.url.endswith("/stream.mp3")


def test_play_intent_can_handle():
    handler = LaunchAndPlayHandler()
    intent = Intent(name="PlayAudioIntent")
    request = IntentRequest(request_id="r2", timestamp="2026-11-19T00:00:00Z", intent=intent)
    handler_input = _build_handler_input(request)

    assert handler.can_handle(handler_input)


def test_stop_handler():
    handler = StopAndCancelHandler()
    intent = Intent(name="AMAZON.StopIntent")
    request = IntentRequest(request_id="r3", timestamp="2026-11-19T00:00:00Z", intent=intent)
    handler_input = _build_handler_input(request)

    assert handler.can_handle(handler_input)
    response = handler.handle(handler_input)

    assert isinstance(response, Response)
    assert len(response.directives) == 2
    assert isinstance(response.directives[0], StopDirective)


def test_help_handler():
    handler = HelpIntentHandler()
    intent = Intent(name="AMAZON.HelpIntent")
    request = IntentRequest(request_id="r4", timestamp="2026-11-19T00:00:00Z", intent=intent)
    handler_input = _build_handler_input(request)

    assert handler.can_handle(handler_input)
    response = handler.handle(handler_input)

    assert "sound river" in response.output_speech.ssml


def test_exception_handler():
    handler = CatchAllExceptionHandler()
    handler_input = _build_handler_input(LaunchRequest(request_id="r5", timestamp="2026-11-19T00:00:00Z"))

    assert handler.can_handle(handler_input, RuntimeError("Test error"))
    response = handler.handle(handler_input, RuntimeError("Test error"))

    assert response.should_end_session is True
