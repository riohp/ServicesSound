import os
from ask_sdk_core.dispatch_components import (
    AbstractExceptionHandler,
    AbstractRequestHandler,
)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_model import Response
from ask_sdk_model.interfaces.audioplayer import (
    AudioItem,
    ClearBehavior,
    ClearQueueDirective,
    PlayBehavior,
    PlayDirective,
    StopDirective,
    Stream,
)

DEFAULT_STREAM_URL = os.environ.get(
    "STREAM_URL", "https://tu-url-de-ngrok.ngrok-free.app/stream.mp3"
)


class LaunchAndPlayHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            is_request_type("LaunchRequest")(handler_input)
            or is_intent_name("PlayAudioIntent")(handler_input)
            or is_intent_name("AMAZON.ResumeIntent")(handler_input)
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        stream_url = os.environ.get("STREAM_URL", DEFAULT_STREAM_URL)
        speech_text = "Conectando al audio de tu computadora."

        play_directive = PlayDirective(
            play_behavior=PlayBehavior.REPLACE_ALL,
            audio_item=AudioItem(
                stream=Stream(
                    url=stream_url,
                    token="services-sound-stream-token",
                    offset_in_milliseconds=0,
                )
            ),
        )

        return (
            handler_input.response_builder.speak(speech_text)
            .add_directive(play_directive)
            .set_should_end_session(True)
            .response
        )


class StopAndCancelHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return (
            is_intent_name("AMAZON.StopIntent")(handler_input)
            or is_intent_name("AMAZON.CancelIntent")(handler_input)
            or is_intent_name("AMAZON.PauseIntent")(handler_input)
        )

    def handle(self, handler_input: HandlerInput) -> Response:
        stop_directive = StopDirective()
        clear_directive = ClearQueueDirective(
            clear_behavior=ClearBehavior.CLEAR_ALL
        )
        return (
            handler_input.response_builder.add_directive(stop_directive)
            .add_directive(clear_directive)
            .set_should_end_session(True)
            .response
        )


class AudioPlayerEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        req_type = handler_input.request_envelope.request.object_type
        return req_type.startswith("AudioPlayer.")

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        speech = "Puedes decir: Alexa, on sound river para iniciar la transmisión de audio."
        return (
            handler_input.response_builder.speak(speech)
            .ask(speech)
            .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input: HandlerInput) -> Response:
        return handler_input.response_builder.response


class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input: HandlerInput, exception: Exception) -> bool:
        return True

    def handle(self, handler_input: HandlerInput, exception: Exception) -> Response:
        speech = "Ocurrió un error al procesar la solicitud. Verifica que la transmisión de tu PC esté activa."
        return (
            handler_input.response_builder.speak(speech)
            .set_should_end_session(True)
            .response
        )


sb = SkillBuilder()
sb.add_request_handler(LaunchAndPlayHandler())
sb.add_request_handler(StopAndCancelHandler())
sb.add_request_handler(AudioPlayerEventHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
