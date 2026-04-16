import inspect
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from pydantic import TypeAdapter

from app.core.redis import redis_client

P = ParamSpec("P")
T = TypeVar("T")


def cache_result[T](key_template: str, schema: type[T]):
    """
    A decorator to cache the result of a service method.
    """
    adapter = TypeAdapter(schema)

    def decorator(
        func: Callable[P, Awaitable[T | None]],
    ) -> Callable[P, Awaitable[T | None]]:
        sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T | None:
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arg_values = bound_args.arguments

            try:
                key = key_template.format(**arg_values)
                if not key:
                    return await func(*args, **kwargs)
            except KeyError:
                return await func(*args, **kwargs)

            cached_data = await redis_client.get(key)
            if cached_data:
                return adapter.validate_python(cached_data)

            result = await func(*args, **kwargs)

            if result is None:
                return None

            serialized_data = adapter.dump_python(result)
            await redis_client.set(key, serialized_data)

            return result

        return wrapper

    return decorator
