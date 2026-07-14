#!/usr/bin/env python3
"""Compare detector migration progress between two Groundlight accounts."""

import os
import time
from typing import Dict, List, Optional

from groundlight import ApiException, Detector, ExperimentalApi

PAGE_SIZE = 100
IQ_COUNT_TIMEOUT = 60
RATE_LIMIT_STATUS = 429
MAX_RATE_LIMIT_RETRIES = 5


def call_with_backoff(func, *args, **kwargs):
    """Call an API function, retrying rate-limit responses with exponential backoff."""
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except ApiException as error:
            if error.status != RATE_LIMIT_STATUS or attempt == MAX_RATE_LIMIT_RETRIES:
                raise
            time.sleep(2**attempt)


def build_client(token_env: str, endpoint_env: str) -> ExperimentalApi:
    """Construct a Groundlight client from API token and endpoint environment variables."""
    api_token = os.environ.get(token_env)
    if not api_token:
        raise SystemExit(f"Missing required environment variable: {token_env}")
    return ExperimentalApi(endpoint=os.environ.get(endpoint_env) or None, api_token=api_token)


def list_all_detectors(client: ExperimentalApi) -> List[Detector]:
    """Return every detector in an account."""
    detectors = []
    page = 1
    while True:
        batch = call_with_backoff(client.list_detectors, page=page, page_size=PAGE_SIZE)
        detectors.extend(batch.results)
        if not batch.next:
            return detectors
        page += 1


def detectors_by_name(detectors: List[Detector], account_name: str) -> Dict[str, Detector]:
    """Index detectors by name, failing if an account contains duplicate names."""
    indexed = {}
    duplicates = set()
    for detector in detectors:
        if detector.name in indexed:
            duplicates.add(detector.name)
        indexed[detector.name] = detector
    if duplicates:
        names = ", ".join(sorted(repr(name) for name in duplicates))
        raise SystemExit(f"Duplicate detector names in {account_name} account: {names}")
    return indexed


def image_query_count(client: ExperimentalApi, detector_id: Optional[str] = None) -> int:
    """Return the account-wide or detector-specific image-query count."""
    params = {"page": 1, "page_size": 1, "_request_timeout": IQ_COUNT_TIMEOUT}
    if detector_id is not None:
        params["detector_id"] = detector_id
    batch = call_with_backoff(client.image_queries_api.list_image_queries, **params)
    return batch.count


def print_section(title: str, rows: List[str]) -> None:
    """Print one detector migration category."""
    print(f"\n{title} ({len(rows)})")
    print("-" * len(title))
    if rows:
        for row in rows:
            print(row)
    else:
        print("None")


def compare_detectors(src: ExperimentalApi, dst: ExperimentalApi) -> None:
    """Compare source detectors with same-named destination detectors by image-query count."""
    src_detectors = list_all_detectors(src)
    dst_detectors = list_all_detectors(dst)
    src_by_name = detectors_by_name(src_detectors, "source")
    dst_by_name = detectors_by_name(dst_detectors, "destination")

    fully_migrated = []
    partially_migrated = []
    not_migrated = []

    for name, src_detector in sorted(src_by_name.items()):
        dst_detector = dst_by_name.get(name)
        if dst_detector is None:
            not_migrated.append(f"{name!r}: src={src_detector.id}")
            continue

        src_count = image_query_count(src, src_detector.id)
        dst_count = image_query_count(dst, dst_detector.id)
        row = (
            f"{name!r}: src={src_detector.id}, dst={dst_detector.id}, "
            f"src IQs={src_count}, dst IQs={dst_count}"
        )
        if src_count == dst_count:
            fully_migrated.append(row)
        else:
            partially_migrated.append(row)

    print(f"Source: {len(src_detectors)} detectors\nDestination: {len(dst_detectors)} detectors")
    print_section("Fully migrated", fully_migrated)
    print_section("Partially migrated", partially_migrated)
    print_section("Not migrated", not_migrated)


def main() -> None:
    """Compare migration progress using source and destination environment credentials."""
    src = build_client("GROUNDLIGHT_API_TOKEN_SRC", "GROUNDLIGHT_ENDPOINT_SRC")
    dst = build_client("GROUNDLIGHT_API_TOKEN_DST", "GROUNDLIGHT_ENDPOINT_DST")
    compare_detectors(src, dst)


if __name__ == "__main__":
    main()
