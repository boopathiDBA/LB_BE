from fastapi import Request, Response
from fastapi.routing import APIRoute
from typing import Callable


class LoggerRouteHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def route_handler(request: Request) -> Response:
            return await original_route_handler(request)

        return route_handler
