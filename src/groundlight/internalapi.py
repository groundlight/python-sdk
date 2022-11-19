import logging
import os
import time
import uuid
from typing import Dict

import model
import requests
from openapi_client.api_client import ApiClient

logger = logging.getLogger("groundlight.sdk")


def _generate_request_id():
    # TODO: use a ksuid instead of a uuid.  Most of our API uses ksuids for lots of reasons.
    # But we don't want to just import ksuid because we want to avoid dependency bloat
    return "req_uu" + uuid.uuid4().hex


class InternalApiException(RuntimeError):
    # TODO: We need a better exception hierarchy
    pass


class GroundlightApiClient(ApiClient):
    """Subclassing the OpenAPI-generated ApiClient to add a bit of custom functionality.
    Not crazy about using polymorphism, but this is simpler than modifying the moustache
    templates in the generator to add the functionality.
    """

    REQUEST_ID_HEADER = "X-Request-Id"

    def call_api(self, *args, **kwargs):
        """Adds a request-id header to each API call."""
        # Note we don't look for header_param in kwargs here, because this method is only called in one place
        # in the generated code, so we can afford to make this brittle.
        header_param = args[4]  # that's the number in the list
        if not header_param:
            # This will never happen in normal useage.
            logger.warning("Can't set request-id because headers not set")
        else:
            if not header_param.get(self.REQUEST_ID_HEADER, None):
                header_param[self.REQUEST_ID_HEADER] = _generate_request_id()
                # Note that we have updated the actual dict in args, so we don't have to put it back in
        return super().call_api(*args, **kwargs)

    #
    # The methods below will eventually go away when we move to properly model
    # these methods with OpenAPI
    #

    def _headers(self) -> dict:
        request_id = _generate_request_id()
        return {
            "Content-Type": "application/json",
            "x-api-token": self.configuration.api_key["ApiToken"],
            "X-Request-Id": request_id,
        }

    def _add_label(self, image_query_id: str, label: str) -> dict:
        """Temporary internal call to add a label to an image query.  Not supported."""
        # TODO: Properly model this with OpenApi spec.
        start_time = time.time()
        url = f"{self.configuration.host}/labels"

        data = {
            "label": label,
            "posicheck_id": image_query_id,
        }

        headers = self._headers()

        logger.info(f"Posting label={label} to image_query {image_query_id} ...")
        response = requests.request("POST", url, json=data, headers=headers)
        elapsed = 1000 * (time.time() - start_time)
        logger.debug(f"Call to ImageQuery.add_label took {elapsed:.1f}ms response={response.text}")

        if response.status_code != 200:
            raise InternalApiException(
                f"Error adding label to image query {image_query_id} status={response.status_code} {response.text}"
            )

        return response.json()
