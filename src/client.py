from typing import AsyncGenerator
from httpx import AsyncClient


async def get_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient() as client:
        yield client
