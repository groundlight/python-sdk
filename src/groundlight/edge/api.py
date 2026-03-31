import time
from http import HTTPStatus

import requests

from groundlight.client import EdgeNotAvailableError
from groundlight.edge.config import EdgeEndpointConfig

_EDGE_METHOD_UNAVAILABLE_HINT = (
    "Make sure the client is pointed at a running edge endpoint "
    "(via GROUNDLIGHT_ENDPOINT env var or the endpoint= constructor arg)."
)


class EdgeAPI:
    """Namespace for edge-endpoint operations, accessed via ``gl.edge``."""

    def __init__(self, client) -> None:
        self._client = client

    def _base_url(self) -> str:
        return self._client.edge_base_url()

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self._base_url()}{path}"
        headers = self._client.get_raw_headers()
        try:
            response = requests.request(
                method, url, headers=headers, verify=self._client.configuration.verify_ssl, timeout=10, **kwargs
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == HTTPStatus.NOT_FOUND:
                raise EdgeNotAvailableError(
                    f"Edge method not available at {url}. {_EDGE_METHOD_UNAVAILABLE_HINT}"
                ) from e
            raise
        except requests.exceptions.ConnectionError as e:
            raise EdgeNotAvailableError(
                f"Could not connect to {self._base_url()}. {_EDGE_METHOD_UNAVAILABLE_HINT}"
            ) from e
        return response

    def get_config(self) -> EdgeEndpointConfig:
        """Retrieve the active edge endpoint configuration."""
        response = self._request("GET", "/edge-config")
        return EdgeEndpointConfig.from_payload(response.json())

    def get_detector_readiness(self) -> dict[str, bool]:
        """Check which configured detectors have inference pods ready to serve.

        :return: Dict mapping detector_id to readiness (True/False).
        """
        response = self._request("GET", "/edge-detector-readiness")
        return {det_id: info["ready"] for det_id, info in response.json().items()}

    def set_config(
        self,
        config: EdgeEndpointConfig,
        timeout_sec: float = 600,
    ) -> EdgeEndpointConfig:
        """Replace the edge endpoint configuration and wait until all detectors are ready.

        :param config: The new configuration to apply.
        :param timeout_sec: Max seconds to wait for all detectors to become ready.
        :return: The applied configuration as reported by the edge endpoint.
        """
        self._request("PUT", "/edge-config", json=config.to_payload())

        poll_interval_seconds = 1
        desired_ids = {d.detector_id for d in config.detectors if d.detector_id}
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            readiness = self.get_detector_readiness()
            if desired_ids and all(readiness.get(did, False) for did in desired_ids):
                return self.get_config()
            time.sleep(poll_interval_seconds)

        raise TimeoutError(
            f"Edge detectors were not all ready within {timeout_sec}s. "
            "The edge endpoint may still be converging, or may have encountered an error."
        )
