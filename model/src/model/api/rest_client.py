import requests
from typing import Optional, List
from requests.exceptions import RequestException, Timeout
import logging

from model.config import config
from model.api.schema_validation.state_schema import StatePayload, validate_state_payload
from model.api.schema_validation.command_schema import CommandPayload

logger = logging.getLogger(__name__)

class HTTPClient:
    """Local HTTP client with built-in schema validation."""

    def __init__(self):
        self.base_url = config.server_url
        self.timeout = config.request_timeout
        self.session = requests.Session()

        self.session.headers.update({"Content-Type": "application/json"})
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=2))

    async def get_state(self) -> Optional[dict]:
        """
        Fetch and validate state from the native, state-collecting server.

        Returns:
            Validated state data or None if failed
        """
        try:
            response = self.session.get(
                f"{self.base_url}/state",
                timeout=self.timeout
            )
            response.raise_for_status()

            state_data = response.json()
            validated_state = validate_state_payload(state_data)

            if validated_state is None:
                logger.warning("Received invalid state data from server")
                return None

            return validated_state.model_dump()

        except (RequestException, ValueError) as e:
            logger.error(f"Failed to get state: {e}")
            return None

    async def send_command(self, validated_command: CommandPayload) -> bool:
        """
        Send validated command to server.
        """
        try:
            response = self.session.post(
                f"{self.base_url}/command",
                json=validated_command.model_dump_json(),
                timeout=self.timeout
            )
            response.raise_for_status()
            return True

        except RequestException as e:
            logger.error(f"Failed to send action {validated_command.action}: {e}")
            return False


# Factory function for easy testing
def create_http_client() -> HTTPClient:
    """Create and configure the HTTP client."""
    return HTTPClient()