import contextlib
import inspect
import logging

from adventurelib import when as _when

from engine.globals import G as _G


@contextlib.contextmanager
def _poll_context(poll_before=True, poll_after=True):
    logging.debug("Polling pre-events.")
    if poll_before:
        for event in _G.events("pre"):
            if event.will_execute:
                event.execute()
    yield
    logging.debug("Polling post-events.")
    if poll_after:
        for event in _G.events("post"):
            if event.will_execute:
                event.execute()


def _add_parameter_strings(parameter, kind_to_argstrings, kind_to_callstrings):
    if parameter.kind in {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    }:
        arg_string = parameter.name
        call_string = parameter.name
    elif parameter.kind is inspect.Parameter.VAR_POSITIONAL:
        arg_string = f"*{parameter.name}"
        call_string = f"*{parameter.name}"
    elif parameter.kind is inspect.Parameter.VAR_KEYWORD:
        arg_string = f"**{parameter.name}"
        call_string = f"**{parameter.name}"
    if parameter.default is not inspect.Parameter.empty:
        arg_string = f"{parameter_string}={parameter.default}"
        call_string = f"{parameter_string}={parameter_string}"
    kind_to_argstrings.setdefault(parameter.kind, []).append(arg_string)
    kind_to_callstrings.setdefault(parameter.kind, []).append(call_string)


def _build_arg_strings(func):
    sig = inspect.signature(func)
    kind_to_argstrings = {}
    kind_to_callstrings = {}
    for _, parameter in sig.parameters.items():
        _add_parameter_strings(parameter, kind_to_argstrings, kind_to_callstrings)

    argument_strings = []
    for parameter_kind in inspect._ParameterKind:
        if parameter_kind is inspect.Parameter.KEYWORD_ONLY and kind_to_argstrings.get(
            parameter_kind
        ):
            argument_strings.append("*")
        argument_strings.extend(kind_to_argstrings.get(parameter_kind, []))
        if (
            parameter_kind is inspect.Parameter.POSITIONAL_ONLY
            and kind_to_argstrings.get(parameter_kind)
        ):
            argument_strings.append("/")

    call_strings = []
    for parameter_kind in inspect._ParameterKind:
        call_strings.extend(kind_to_callstrings.get(parameter_kind, []))

    return ", ".join(argument_strings), ", ".join(call_strings)


def when(command, context=None, **kwargs):
    def decorator(func):
        arg_string, call_string = _build_arg_strings(func)
        logging.debug(f"arg_string: {arg_string}")
        logging.debug(f"call_string: {call_string}")
        these_globals = {
            "_poll_context": _poll_context,
            "logging": logging,
            "poll_before": kwargs.pop("poll_before", False),
            "poll_after": kwargs.pop("poll_after", False),
            "func": func,
        }
        these_locals = {}

        exec(
            f"""def wrapped({arg_string}):
            with _poll_context():
                logging.debug("returning from context")
                return func({call_string})""",
            these_globals,
            these_locals,
        )

        return _when(command, context=context, **kwargs)(these_locals["wrapped"])

    return decorator
