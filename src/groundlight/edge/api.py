import time
from http import HTTPStatus

import requests

from groundlight.client import EdgeDetectorsNotReadyError, EdgeNotAvailableError
from groundlight.edge.config import EdgeEndpointConfig

_EDGE_METHOD_UNAVAILABLE_HINT = (
    "Make sure the client is pointed at a running Edge Endpoint "
    "(via GROUNDLIGHT_ENDPOINT env var or the endpoint= constructor arg)."
)

DEFAULT_EDGE_READY_TIMEOUT_SEC = 600.0


class EdgeEndpointApi:
    """
    Namespace for operations that are specific to the Edge Endpoint,
    such as setting and getting the EdgeEndpoint configuration.

    Currently only available through :class:`~groundlight.ExperimentalApi`. Accessed via the
    ``edge`` attribute::

        gl = ExperimentalApi()
        gl.edge.set_config(config)
    """

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

    def get_upstream_endpoint(self) -> str:
        """Return the origin of the Groundlight cloud this Edge Endpoint forwards to, e.g. ``https://api.groundlight.ai``.

        :raises EdgeNotAvailableError: If the client is not pointed at an Edge Endpoint that supports this.
        """
        response = self._request("GET", "/edge-info")
        try:
            return response.json()["upstream_endpoint"]
        except (ValueError, KeyError, TypeError) as e:
            raise EdgeNotAvailableError(
                f"Unexpected response from {self._base_url()}/edge-info. {_EDGE_METHOD_UNAVAILABLE_HINT}"
            ) from e

    def apply_config(self, config: EdgeEndpointConfig) -> None:
        """Replace the edge endpoint configuration and return without waiting for detectors to serve.

        Call wait_detectors to wait until specific detectors are serving. set_config does both.
        """
        if config is None:
            raise TypeError("apply_config requires an EdgeEndpointConfig")
        self._request("PUT", "/edge-config", json=config.to_payload())

    def wait_detectors(
        self,
        detector_ids: list[str],
        timeout_sec: float = DEFAULT_EDGE_READY_TIMEOUT_SEC,
    ) -> None:
        """Wait until every given detector is serving.

        Does not change the configuration. An empty list returns immediately. A timeout of 0 or less waits 10 minutes.

        :raises EdgeDetectorsNotReadyError: If some detectors are still down when the timeout elapses.
        """
        wanted = list(detector_ids)
        if not wanted:
            return
        timeout_sec = self._resolved_ready_timeout(timeout_sec)
        deadline = time.time() + timeout_sec
        pending: list[str] = wanted
        while time.time() < deadline:
            readiness = self.get_detector_readiness()
            pending = [did for did in wanted if not readiness.get(did, False)]
            if not pending:
                return
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            time.sleep(min(1.0, remaining))
        raise EdgeDetectorsNotReadyError(
            f"Edge detectors were not all ready within {timeout_sec}s: {pending} still down."
        )

    def set_config(
        self,
        config: EdgeEndpointConfig,
        timeout_sec: float = DEFAULT_EDGE_READY_TIMEOUT_SEC,
    ) -> EdgeEndpointConfig:
        """Replace the edge endpoint configuration and wait until all detectors are ready.

        This calls apply_config, then wait_detectors for the detectors in the config, then get_config.
        A config with no detectors skips the wait. If the wait times out, the configuration has still been applied.
        A timeout of 0 or less waits 10 minutes.

        :return: The configuration reported by the edge endpoint.
        """
        self.apply_config(config)
        try:
            self.wait_detectors([d.detector_id for d in config.detectors], timeout_sec=timeout_sec)
        except EdgeDetectorsNotReadyError as e:
            raise EdgeDetectorsNotReadyError(
                f"{e} The configuration has been applied; the edge endpoint may still be converging."
            ) from e
        return self.get_config()

    @staticmethod
    def _resolved_ready_timeout(timeout_sec: float) -> float:
        if timeout_sec <= 0:
            return DEFAULT_EDGE_READY_TIMEOUT_SEC
        return timeout_sec
