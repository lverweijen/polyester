from collections.abc import Iterator, Iterable
from typing import Any, Protocol, Literal

__all__ = ["TemplateLike", "InterpolationLike", "convert"]


try:
    # Python 3.14 or newer
    from string.templatelib import convert
except ImportError:
    # Older python versions
    from tstr import convert


class InterpolationLike(Protocol):
    value: Any
    format_spec: str
    conversion: Literal["a", "r", "s"] | None


class TemplateLike(Protocol, Iterable[str | InterpolationLike]):
    def __iter__(self) -> Iterator[str | InterpolationLike]:
        return iter([])
