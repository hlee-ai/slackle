from typing import Any, Dict, Optional, Type, TypeVar

from slackle.exc import FormatterNotFoundError

from .types import BaseFormatter

T = TypeVar("T")
T_Formatter = TypeVar("T_Formatter", bound=BaseFormatter)


class Formatter:
    def __init__(self):
        self._registry: Dict[Type[Any], Type[BaseFormatter]] = {}

    def __contains__(self, data_type: Type[Any]) -> bool:
        return data_type in self._registry

    def __getitem__(self, data_type: Type[T]) -> Type[BaseFormatter]:
        if data_type not in self._registry:
            raise FormatterNotFoundError(data_type)
        return self._registry[data_type]

    def __iter__(self):
        return iter(self._registry.items())

    def __len__(self):
        return len(self._registry)

    def __repr__(self):
        return f"<Formatter registered: {list(self._registry.keys())}>"

    def __str__(self):
        return f"<Formatter {len(self)} formatters>"

    def register(self, data_type: Type[T], *, override: bool = False):
        """
        Register a formatter for a specific data type.
        Usage:
            @formatter.register(MyData)
            class MyFormatter(BaseFormatter[MyData, MyParams]):
                ...
        """

        def decorator(cls: Type[T_Formatter]) -> Type[T_Formatter]:
            if not issubclass(cls, BaseFormatter):
                raise TypeError("Registered class must subclass BaseFormatter")

            if data_type in self._registry and not override:
                print(
                    f"Warning: formatter for {data_type} already registered. "
                    f"Use override=True to force."
                )
            self._registry[data_type] = cls
            return cls

        return decorator

    def unregister(self, data_type: Type[T]):
        self._registry.pop(data_type, None)

    def get(self, data_type: Type[T]) -> Optional[Type[BaseFormatter]]:
        return self._registry.get(data_type)

    def all(self) -> Dict[Type[Any], Type[BaseFormatter]]:
        return self._registry.copy()

    def has(self, data_type: Type[T]) -> bool:
        return data_type in self._registry

    def update_from(self, other: "Formatter") -> None:
        """
        Merge another formatter registry into this one.

        :param other: Another Formatter instance to merge from
        """
        self._registry.update(other.all())


__all__ = ["Formatter"]
