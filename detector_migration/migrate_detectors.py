#!/usr/bin/env python3
"""
Migrate detectors and their image queries from one Groundlight account to another.

Credentials for the two accounts are read from environment variables so that both a source and a
destination client can be constructed in the same process:

    GROUNDLIGHT_API_TOKEN_SRC
    GROUNDLIGHT_API_TOKEN_DST
    GROUNDLIGHT_ENDPOINT_SRC   (optional, defaults to the standard Groundlight cloud endpoint)
    GROUNDLIGHT_ENDPOINT_DST   (optional, defaults to the standard Groundlight cloud endpoint)

Usage::

    python detector_migration/migrate_detectors.py det_abc123 det_def456
    python detector_migration/migrate_detectors.py --limit 500   # migrate every detector in the source account
"""

import argparse
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Iterator, List, Optional, Set, Tuple, Union

from groundlight import (
    ApiException,
    BinaryClassificationResult,
    BoundingBoxResult,
    CountingResult,
    Detector,
    ExperimentalApi,
    ImageQuery,
    ModeEnum,
    MultiClassificationResult,
    NotFoundError,
)

logger = logging.getLogger("migrate_detectors")

BATCH_SIZE = 2
RATE_LIMIT_STATUS = 429
MAX_RATE_LIMIT_RETRIES = 5


@contextmanager
def timed(label: str) -> Iterator[None]:
    """Log how long the wrapped block of code took to run, for tracking down slow requests."""
    start = time.monotonic()
    try:
        yield
    finally:
        logger.info("%s took %.2fs", label, time.monotonic() - start)


def call_with_backoff(func, *args, **kwargs):
    """Call func(*args, **kwargs), retrying with exponential backoff if the API responds with a 429 rate limit."""
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except ApiException as e:
            if e.status != RATE_LIMIT_STATUS or attempt == MAX_RATE_LIMIT_RETRIES:
                raise
            delay = 2**attempt
            logger.warning(
                "Rate limited on %s (attempt %d/%d), retrying in %ds",
                getattr(func, "__name__", func),
                attempt + 1,
                MAX_RATE_LIMIT_RETRIES,
                delay,
            )
            time.sleep(delay)


def get_pipeline_config_info(src: ExperimentalApi, detector_id: str) -> Tuple[Optional[str], Optional[str]]:
    """Return the (pipeline_config, edge_pipeline_config) of a detector's active and edge ML pipelines."""
    pipeline_config = None
    edge_pipeline_config = None
    page = 1
    while True:
        with timed(f"list_detector_pipelines({detector_id}, page={page})"):
            batch = call_with_backoff(src.list_detector_pipelines, detector_id, page=page, page_size=50)
        for pipeline in batch.results:
            if pipeline.is_active_pipeline:
                pipeline_config = pipeline.pipeline_config
            if pipeline.is_edge_pipeline:
                edge_pipeline_config = pipeline.pipeline_config
        if not batch.next:
            return pipeline_config, edge_pipeline_config
        page += 1


def build_client(token_env: str, endpoint_env: str) -> ExperimentalApi:
    """Construct a Groundlight client from a pair of environment variables holding its API token and endpoint."""
    api_token = os.environ.get(token_env)
    if not api_token:
        raise SystemExit(f"Missing required environment variable: {token_env}")
    endpoint = os.environ.get(endpoint_env) or None
    return ExperimentalApi(endpoint=endpoint, api_token=api_token)


def all_detector_ids(client: ExperimentalApi, page_size: int) -> List[str]:
    """Return the IDs of every detector in the account, by paging through list_detectors."""
    ids = []
    page = 1
    while True:
        with timed(f"list_detectors(page={page})"):
            batch = call_with_backoff(client.list_detectors, page=page, page_size=page_size)
        ids.extend(detector.id for detector in batch.results)
        if not batch.next:
            return ids
        page += 1


def create_matching_detector(src: ExperimentalApi, dst: ExperimentalApi, src_detector: Detector) -> Detector:
    """Find or create a destination detector matching a source detector's name, mode, and configuration.

    Hand-rolled because the SDK's Groundlight.get_or_create_detector() convenience method only
    supports BINARY mode (it has no mode/class_names parameters), so it can't be used here directly.
    """
    try:
        with timed(f"get_detector_by_name({src_detector.name!r})"):
            return call_with_backoff(dst.get_detector_by_name, src_detector.name)
    except NotFoundError:
        pass

    pipeline_config, edge_pipeline_config = get_pipeline_config_info(src, src_detector.id)
    common = {
        "name": src_detector.name,
        "query": src_detector.query,
        "group_name": src_detector.group_name,
        "confidence_threshold": src_detector.confidence_threshold,
        "patience_time": src_detector.patience_time,
        "pipeline_config": pipeline_config,
        "edge_pipeline_config": edge_pipeline_config,
        "metadata": {"migrated_from_detector": src_detector.id},
    }
    mode_config = src_detector.mode_configuration or {}

    with timed(f"create_detector({src_detector.name!r}, mode={src_detector.mode})"):
        if src_detector.mode == ModeEnum.BINARY:
            return call_with_backoff(dst.create_binary_detector, **common)
        if src_detector.mode == ModeEnum.COUNT:
            max_count = mode_config.get("max_count")
            return call_with_backoff(
                dst.create_counting_detector,
                class_name=mode_config["class_name"],
                max_count=int(max_count) if max_count is not None else None,
                **common,
            )
        if src_detector.mode == ModeEnum.MULTI_CLASS:
            return call_with_backoff(dst.create_multiclass_detector, class_names=mode_config["class_names"], **common)
        if src_detector.mode == ModeEnum.BOUNDING_BOX:
            max_num_bboxes = mode_config.get("max_num_bboxes")
            return call_with_backoff(
                dst.create_bounding_box_detector,
                class_name=mode_config["class_name"],
                max_num_bboxes=int(max_num_bboxes) if max_num_bboxes is not None else None,
                **common,
            )
        if src_detector.mode == ModeEnum.TEXT:
            return call_with_backoff(dst.create_text_recognition_detector, **common)
        raise ValueError(f"Unsupported detector mode: {src_detector.mode}")


def label_for_result(image_query: ImageQuery) -> Optional[Union[str, int]]:
    """Extract the ground-truth label value to pass to add_label for a completed image query.

    Returns None if the result type has no supported ground-truth label (e.g. text recognition).
    """
    result = image_query.result
    if result is None:
        return None
    if isinstance(result, CountingResult):
        return result.count
    if isinstance(result, (BinaryClassificationResult, MultiClassificationResult, BoundingBoxResult)):
        return result.label
    return None


def already_migrated_iq_ids(dst: ExperimentalApi, dst_detector_id: str, page_size: int) -> Set[str]:
    """Collect the source image query IDs already migrated to a destination detector.

    Scans the destination detector's existing image queries for the migrated_from_iq metadata tag that
    migrate_image_query attaches on submission, so a re-run of this script can skip them.
    """
    migrated_ids = set()
    page = 1
    while True:
        with timed(f"list_image_queries(dst, page={page})"):
            batch = call_with_backoff(
                dst.list_image_queries, page=page, page_size=page_size, detector_id=dst_detector_id
            )
        for image_query in batch.results:
            src_iq_id = (image_query.metadata or {}).get("migrated_from_iq")
            if src_iq_id:
                migrated_ids.add(src_iq_id)
        if not batch.next:
            return migrated_ids
        page += 1


def _byte_length(data: Union[bytes, None]) -> int:
    """Return the byte length of `data`, which may be raw bytes or a seekable file-like object.

    `Groundlight.get_image()` is annotated as returning bytes, but actually returns an open file
    handle (the OpenAPI client writes binary responses to a temp file), so plain `len()` doesn't work.
    """
    if data is None:
        return 0
    if isinstance(data, bytes):
        return len(data)
    pos = data.tell()
    data.seek(0, os.SEEK_END)
    size = data.tell()
    data.seek(pos)
    return size


def migrate_image_query(src: ExperimentalApi, dst: ExperimentalApi, src_iq: ImageQuery, dst_detector: Detector) -> None:
    """Copy one image query's image, and its ground-truth label if fully confident, to a destination detector."""
    image_bytes = None
    try:
        with timed(f"get_image({src_iq.id})"):
            image_data = call_with_backoff(src.get_image, src_iq.id)
            image_bytes = image_data if isinstance(image_data, bytes) else image_data.read()
        with timed(f"ask_async({src_iq.id})"):
            # ask_async skips synchronous ML inference on the destination server, which we don't need
            # since we're only using the returned image query id to attach our own ground-truth label.
            dst_iq = call_with_backoff(
                dst.ask_async,
                detector=dst_detector,
                image=image_bytes,
                human_review="NEVER",
                metadata={"migrated_from_iq": src_iq.id, "migrated_from_detector": src_iq.detector_id},
            )
        if src_iq.result is not None and src_iq.result.confidence == 1.0:
            label = label_for_result(src_iq)
            if label is not None:
                with timed(f"add_label({dst_iq.id})"):
                    call_with_backoff(dst.add_label, dst_iq, label, rois=src_iq.rois or None)
    except ApiException:
        size = _byte_length(image_bytes)
        logger.error("Failed to migrate source image query %s (image was %d bytes)", src_iq.id, size)
        raise


def migrate_detector(
    src: ExperimentalApi, dst: ExperimentalApi, src_detector_id: str, limit: Optional[int], page_size: int
) -> None:
    """Migrate one detector and, up to limit, its not-yet-migrated image queries to the destination account."""
    with timed(f"get_detector({src_detector_id})"):
        src_detector = call_with_backoff(src.get_detector, src_detector_id)
    dst_detector = create_matching_detector(src, dst, src_detector)
    logger.info("Detector %s (%r) -> %s (%r)", src_detector.id, src_detector.name, dst_detector.id, dst_detector.name)

    skip_ids = already_migrated_iq_ids(dst, dst_detector.id, page_size)
    logger.info("%d image queries already migrated to this detector", len(skip_ids))

    migrated = 0
    page = 1
    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        while limit is None or migrated < limit:
            with timed(f"list_image_queries(src, page={page})"):
                batch = call_with_backoff(
                    src.list_image_queries, page=page, page_size=page_size, detector_id=src_detector.id
                )
            to_migrate = [iq for iq in batch.results if iq.id not in skip_ids]
            if limit is not None:
                to_migrate = to_migrate[: limit - migrated]
            futures = [executor.submit(migrate_image_query, src, dst, iq, dst_detector) for iq in to_migrate]
            for future in futures:
                future.result()
            migrated += len(to_migrate)
            if not batch.next:
                break
            page += 1
    logger.info("Migrated %d new image queries for detector %s", migrated, src_detector.id)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the migration script."""
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "detector_ids",
        nargs="*",
        help="Source detector IDs to migrate. If omitted, migrates every detector in the source account.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of new image queries to migrate per detector. Default: no limit.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="Page size to use when paginating detectors and image queries. Default: 100.",
    )
    return parser.parse_args()


def main() -> None:
    """Migrate the requested (or all) detectors and their image queries from the source to destination account."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = parse_args()

    src = build_client("GROUNDLIGHT_API_TOKEN_SRC", "GROUNDLIGHT_ENDPOINT_SRC")
    dst = build_client("GROUNDLIGHT_API_TOKEN_DST", "GROUNDLIGHT_ENDPOINT_DST")

    detector_ids = args.detector_ids or all_detector_ids(src, args.page_size)
    logger.info("Migrating %d detector(s)", len(detector_ids))

    for detector_id in detector_ids:
        migrate_detector(src, dst, detector_id, args.limit, args.page_size)


if __name__ == "__main__":
    main()
