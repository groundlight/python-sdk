import logging
import time
import uuid
from typing import Dict

import model
import requests

from groundlight.config import GROUNDLIGHT_ENDPOINT

logger = logging.getLogger("groundlight.sdk")

def _request_id():
    # I kinda hate myself right now for doing this
    return "req_notaksuid" + uuid.uuid4().hex


def _headers() -> dict:
    request_id = _request_id()
    logger.debug(f"Setting {request_id=}")
    return {
        "Content-Type": "application/json",
        "x-api-token": os.environ["GROUNDLIGHT_API_TOKEN"],
        "X-Request-Id": request_id,
    }


class InternalSdkException(RuntimeError):
    pass


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
            raise InternalSdkException(f"Error adding label to {image_query_id=} status={response.status_code} {response.text}")

        return response.json()
