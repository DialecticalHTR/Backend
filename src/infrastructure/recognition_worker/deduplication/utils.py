import inspect
from typing import Callable


def add_parameters(function: Callable, new_paramaters: list[inspect.Parameter]) -> Callable:
    signature = inspect.signature(function)
    annotations = inspect.get_annotations(function)

    parameter_kinds: dict[inspect._ParameterKind, list[inspect.Parameter]] = {}

    for _, param in signature.parameters.items():
        parameter_kinds.setdefault(param.kind, []).append(param)
    
    for new_param in new_paramaters:
        parameter_kinds.setdefault(new_param.kind, []).append(new_param)

        if new_param.name in annotations:
            raise ValueError(f"Conflicting parameter name: {new_param.name}")
        if new_param.annotation is not None:
            annotations[new_param.name] = new_param.annotation     
    
    if len(parameter_kinds.get(inspect.Parameter.VAR_POSITIONAL, [])) > 1:
        raise ValueError("Can't have more than 1 VAR_POSITIONAL parameters")
    if len(parameter_kinds.get(inspect.Parameter.VAR_KEYWORD, [])) > 1:
        raise ValueError("Can't have more than 1 VAR_KEYWORD parameters")
    
    combined_paramaters = []
    combined_paramaters.extend(parameter_kinds.get(inspect.Parameter.POSITIONAL_ONLY, []))
    combined_paramaters.extend(parameter_kinds.get(inspect.Parameter.POSITIONAL_OR_KEYWORD, []))
    combined_paramaters.extend(parameter_kinds.get(inspect.Parameter.VAR_POSITIONAL, []))
    combined_paramaters.extend(parameter_kinds.get(inspect.Parameter.KEYWORD_ONLY, []))
    combined_paramaters.extend(parameter_kinds.get(inspect.Parameter.VAR_KEYWORD, []))

    new_signature = inspect.Signature(
        parameters=combined_paramaters,
    )
    function.__signature__ = new_signature
    function.__annotations__ = annotations

    return function
