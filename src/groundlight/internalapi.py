import logging
import os
import time
import uuid
from typing import Dict

import model
import requests
from openapi_client.api_client import ApiClient

from groundlight.config import GROUNDLIGHT_ENDPOINT

logger = logging.getLogger("groundlight.sdk")


def _generate_request_id():
    # TODO: use a ksuid instead of a uuid
    return "req_uu" + uuid.uuid4().hex


def _headers() -> dict:
    request_id = _generate_request_id()
    logger.debug(f"Setting {request_id=}")
    return {
        "Content-Type": "application/json",
        # TODO: token needs to come from the Groundlight client.
        # First instinct is to make it a thread-local singleton
        "x-api-token": os.environ["GROUNDLIGHT_API_TOKEN"],
        "X-Request-Id": request_id,
    }


class InternalSdkException(RuntimeError):
    # TODO: We need a better exception hierarchy
    pass


class GroundlightApiClient(ApiClient):
    """Subclassing the OpenAPI-generated ApiClient to add a bit of custom functionality.
    Not crazy about using polymorphism, but this is simpler than modifying the moustache
    templates in the generator to add the functionality.
    """

    REQUEST_ID_HEADER = "X-Request-Id"

    def dont_call_api(self, *args, **kwargs):
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


class ImageQuery(model.ImageQuery):
    def add_label(self, label: str) -> Dict:
        image_query_id = self.id
        start_time = time.time()
        url = f"{GROUNDLIGHT_ENDPOINT}/labels"

        data = {
            "label": label,
            "posicheck_id": image_query_id,
        }

        logger.info(f"Posting {label=} to {image_query_id=} ...")
        response = requests.request("POST", url, json=data, headers=_headers())
        elapsed = 1000 * (time.time() - start_time)
        logger.debug(f"Call to ImageQuery.add_label took {elapsed:.1f}ms {response.text=}")

        if response.status_code != 200:
            raise InternalSdkException(
                f"Error adding label to {image_query_id=} status={response.status_code} {response.text}"
            )

        return response.json()
