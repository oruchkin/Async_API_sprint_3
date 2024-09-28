import inspect
from contextlib import AsyncExitStack
from typing import Any, Callable

from fastapi import FastAPI, Request
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from fastapi.exceptions import ValidationException


async def solve_and_run(command: Callable[[Any], Any], name: str, _app: FastAPI) -> Any:
    """Given a callable, will solve its dependencies and run it."""

    async with AsyncExitStack() as cm:
        request = Request({"type": "http", "headers": [], "query_string": "", "fastapi_astack": cm})
        request.scope["app"] = _app

        dependant = get_dependant(path=f"command:{name}", call=command)

        dep = await solve_dependencies(
            request=request,
            dependant=dependant,
            async_exit_stack=cm,
            dependency_overrides_provider=_app,
            embed_body_fields=False,
        )
        if dep.errors:
            raise ValidationException(dep.errors)
        if not dependant.call:
            raise ValueError("Could not find a callable to run")
        if inspect.iscoroutinefunction(dependant.call):
            result = await dependant.call(**dep.values)
        else:
            result = dependant.call(**dep.values)

        return result
