import aiohttp
from typing import Optional
import logging

from model.config import config
from model.api.schema_validation.state_schema import StatePayload, validate_state_payload
from model.api.schema_validation.command_schema import CommandPayload

logger = logging.getLogger(__name__)

class HTTPClient:
    """Local HTTP client with built-in schema validation."""

    def __init__(self, server_url: str, request_timeout: int):
        self.base_url = server_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=request_timeout)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()


    async def get_state(self) -> Optional[dict]:
        """
        Fetch and validate state from the native, state-collecting server.

        Returns:
            Validated state data or None if failed
        """
        try:
            url = f"{self.base_url}/state"
            async with self.session.get(url) as response:
                response.raise_for_status()
                state_data = await response.json()
                validated_state = validate_state_payload(state_data)

                if validated_state is None:
                    logger.debug("Received invalid state data from server")
                    return None

                return validated_state.model_dump()

        except Exception as e:
            logger.debug(f"Failed to fetch state data from server: {e}")
            return None

    async def send_command(self, validated_command: CommandPayload) -> bool:
        """
        Send validated command to server.
        """
        try:
            url = f"{self.base_url}/command"
            payload = validated_command.model_dump()
            async with self.session.post(url, json=payload) as response:
                response.raise_for_status()
                return True
        except Exception as e:
            logger.debug(f"Failed to send command to server: {e}")
            return False

