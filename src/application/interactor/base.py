import abc
from typing import Generic, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


class BaseInteractor(abc.ABC, Generic[P, R]):
    """
    Basically Callable[..., Any] as an abstract class
    Needed for InteractorFactory as dishka requires a class instead of type hint
    """

    @abc.abstractmethod
    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        ...
