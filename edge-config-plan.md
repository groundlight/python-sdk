# Plan: Edge Configuration via SDK

## Goal

Add a method to the Python SDK that can send configuration to a Groundlight Edge Endpoint,
and optionally wait until the configuration is fully applied (inference pods are ready).
When the SDK is pointed at the cloud API, calling this method should raise an error.

## Decisions

| Question | Decision |
|---|---|
| Config schema | Freeform JSON for now; model it later |
| Runtime effect | Apply immediately: update in-memory config + persist to shared PVC file + write DB records for model updater |
| Method placement | `ExperimentalApi` |
| Auth | Yes, require API token |
| Naming | `configure_edge` with kwargs: `global_config`, `edge_inference_configs`, `detectors`, `wait` |
| OpenAPI spec | Hand-coded HTTP request (like `create_note`); **not** in `public-api.yaml` |
| Waiting strategy | SDK polls `GET /status/metrics.json` for detector readiness |
| Config persistence | Runtime config written to YAML file on shared PVC; read on startup by all containers |

---

## Implemented

### Edge Endpoint: `POST /device-api/v1/edge/configure`

**File**: `app/api/routes/edge_config.py`, registered in `app/api/api.py`

Currently supports **merge mode only**: incoming config is merged into the existing config.

On receiving a config POST, the handler:
1. Merges incoming JSON into the existing `RootEdgeConfig` (global_config, edge_inference_configs, detectors)
2. Validates the merged config via Pydantic (returns 400 on invalid config)
3. Updates `AppState.edge_config` and re-resolves detector inference configs on the `EdgeInferenceManager`
4. Sets up inference client URLs and escalation tracking for new detectors
5. Writes database records for new detectors so the model updater (separate container)
   discovers them and creates Kubernetes inference deployments
6. Persists the merged config to `runtime-edge-config.yaml` on the shared PVC

### Config Persistence (PVC file)

**Problem**: The edge endpoint runs multiple uvicorn workers, plus a separate status-monitor
and model-updater container. An in-memory-only config update only affects the worker that
handles the POST. The status page and other processes see stale config from the original
ConfigMap.

**Solution**: After every successful config update, the merged `RootEdgeConfig` is written
to `runtime-edge-config.yaml` on the shared PVC (`edge-endpoint-pvc`). On startup,
`load_edge_config()` checks for this file before falling back to the ConfigMap.

**File locations** (`app/core/file_paths.py`):
- `/opt/groundlight/edge/sqlite/runtime-edge-config.yaml` (sqlite PVC mount)
- `/opt/groundlight/edge/serving/model-repo/runtime-edge-config.yaml` (model-repo PVC mount)

The loader checks all known mount points so any container can find the file regardless
of which PVC subdirectory it has mounted.

**Load priority** (`app/core/edge_config_loader.py`):
1. `EDGE_CONFIG` environment variable (inline YAML) -- highest priority
2. Runtime config file on shared PVC
3. Default ConfigMap file at `/etc/groundlight/edge-config/edge-config.yaml`

### Python SDK: `ExperimentalApi.configure_edge()`

**File**: `src/groundlight/experimental_api.py`

- Keyword-only args: `global_config`, `edge_inference_configs`, `detectors`, `wait`
- `wait` defaults to 600 seconds (10 minutes)
- POSTs to `{endpoint}/v1/edge/configure`; 404 -> `GroundlightClientError`
- If `wait > 0` and `detectors` provided, polls `GET {base_url}/status/metrics.json`
  every 5 seconds until all configured detectors have `status: "ready"`, or raises on timeout
- Direct `requests.post()` call, not OpenAPI-generated

### End-to-End Flow (merge mode)

1. SDK POSTs config to edge endpoint
2. Edge endpoint merges incoming config with existing config
3. Edge endpoint updates in-memory `AppState` (affects image query behavior immediately on that worker)
4. Edge endpoint persists merged config to `runtime-edge-config.yaml` on shared PVC
5. Edge endpoint writes DB records for new detectors
6. Model updater (separate container) discovers new detectors from DB on next refresh cycle
7. Model updater fetches models and creates Kubernetes inference deployments
8. Pods roll out (~70s)
9. SDK polls `/status/metrics.json` -- status monitor reads runtime config from PVC and reports pod readiness via Kubernetes API
10. All detectors show `status: "ready"` -> SDK returns

### Cloud vs. Edge Detection

| Scenario | What happens |
|---|---|
| SDK -> cloud (`api.groundlight.ai`) | Cloud returns 404 -> SDK raises error |
| SDK -> edge endpoint (with new route) | FastAPI handles it -> returns 200 |
| SDK -> old edge endpoint (without new route) | FastAPI returns 404 -> nginx falls back to cloud -> 404 -> SDK raises error |

---

## Planned: Replace Mode

### Problem

The current merge mode can only **add or update** detectors. It cannot remove detectors
that are no longer desired. If a user wants to go from 5 detectors to 3, the old 2
detectors' inference pods keep running and wasting resources.

### Proposed SDK Change

Add a `replace` parameter to `configure_edge()`:

- `replace=False` (default): Current merge behavior. Incoming config is merged into existing.
- `replace=True`: Incoming config fully replaces the existing config. Detectors not in the
  new config are removed (their inference pods are deleted).

### Required Edge Endpoint Changes

The edge endpoint currently has **no code to delete** Kubernetes Deployments, Services,
database records, or model files for detectors. All of this needs to be added.

**Existing infrastructure we can use:**
- `get_edge_inference_deployment_name(detector_id)` and `get_edge_inference_service_name(detector_id)`
  in `app/core/edge_inference.py` map detector IDs to K8s resource names.
- The service account (`edge-endpoint-service-account`) already has RBAC permissions to
  `delete` both `deployments` and `services`. These permissions are currently unused.
- `InferenceDeploymentManager` in `app/core/kubernetes_management.py` already has a K8s
  client and namespace context. Adding a `delete_inference_deployment()` method here is natural.
- `get_detector_models_dir(repository_root, detector_id)` returns the model directory
  (`{MODEL_REPOSITORY_PATH}/{detector_id}/`). Deleting this directory removes all model
  files (primary + oodd + all versions).

**What needs to be built:**

1. **`InferenceDeploymentManager.delete_inference_deployment(detector_id, is_oodd)`**
   (`app/core/kubernetes_management.py`)
   - Call `delete_namespaced_deployment()` to remove the inference Deployment
   - Call `delete_namespaced_service()` to remove the inference Service
   - The naming functions already exist to map detector ID -> resource names

2. **`DatabaseManager.delete_inference_deployment_record(model_name)`**
   (`app/core/database.py`)
   - Delete the DB record so the model updater doesn't recreate the deployment on its
     next refresh cycle

3. **Model file cleanup**
   - Delete `{MODEL_REPOSITORY_PATH}/{detector_id}/` (the entire detector directory,
     which contains `primary/` and `oodd/` subdirs with versioned model files)
   - Can use `shutil.rmtree()` (already used by `delete_model_version()`)

4. **Replace logic in `edge_config.py` handler**
   - Accept a `replace` flag in the POST body
   - If `replace=True`: use the incoming config as-is instead of merging
   - Diff old vs new detector sets: `removed = old_detector_ids - new_detector_ids`
   - **Deletion must complete before new pods roll out.** The edge endpoint must wait
     for removed detector pods to fully terminate (not just in `Terminating` state)
     before writing DB records for new detectors. This prevents OOM from old and new
     pods competing for the same finite GPU/memory resources.
   - For each removed detector:
     a. Call `InferenceDeploymentManager.delete_inference_deployment()` (primary + oodd)
     b. Poll until the pods are fully gone (not just Terminating)
     c. Call `DatabaseManager.delete_inference_deployment_record()` (primary + oodd)
     d. Delete model files from disk
     e. Clean up `EdgeInferenceManager` state (inference_client_urls, oodd URLs,
        escalation tracking)
   - After all deletions complete: proceed with new/retained detectors (same flow as
     current merge mode)
   - `configure_edge(detectors=[], replace=True)` is valid and removes all detector pods.

5. **SDK changes**
   - Add `replace: bool = False` parameter to `configure_edge()`
   - Pass `replace` flag in POST body
   - When `replace=True` and `wait > 0`: wait for removed pods to terminate AND for
     new/retained pods to become ready

### Ordering Guarantee

When `replace=True`, the edge endpoint enforces this sequence:

```
1. Delete removed detector deployments/services
2. Wait for removed pods to fully terminate
3. Clean up DB records + model files for removed detectors
4. Write DB records for new detectors
5. Model updater picks up new detectors and creates deployments
```

This ensures old pods release their resources before new pods are scheduled,
preventing resource exhaustion on memory/GPU-constrained edge devices.

### Decisions

- **Async**: The POST handler returns immediately. Deletion and re-creation happen
  in a FastAPI background task. The SDK polls `/status/metrics.json` for completion.
- **Termination time**: Inference pods use the K8s default of 30s
  `terminationGracePeriodSeconds`. No custom value is set.
- **Partial failure**: Error out. If deletion of any detector fails, the background
  task logs the error and stops. The config is left in a partially cleaned state;
  the user can retry.

### Implementation Details

**Edge endpoint needs an `InferenceDeploymentManager` on `AppState`.**
Currently only the model-updater container creates one. The edge-endpoint container
has the K8s service account and RBAC permissions but doesn't use them. We add
an `InferenceDeploymentManager` to `AppState`, guarded by the existing
`DEPLOY_DETECTOR_LEVEL_INFERENCE` env var (only set in K8s, not Docker tests).

**Background task flow** (runs after POST returns):
1. Delete K8s Deployments + Services for each removed detector
2. Poll until pods are fully terminated (not just Terminating)
3. Delete DB records for removed detectors
4. Delete model files from PVC (`shutil.rmtree({MODEL_REPOSITORY_PATH}/{detector_id}/`)
5. Write DB records for new detectors (model updater picks these up)

**SDK polling**: When `replace=True` and `wait > 0`, the SDK waits until:
- Removed detector IDs no longer appear in `/status/metrics.json`
- New/retained detector IDs all show `status: "ready"`

---

## Known Limitations

- **Multiprocess in-memory state**: Edge endpoint runs multiple uvicorn workers. The in-memory
  config update only applies to the worker that handles the POST. Other workers retain stale
  in-memory config until they restart. However, on restart they pick up the persisted runtime
  config from the PVC file.
- **Model updater refresh**: The model updater checks for new detectors every `refresh_rate`
  seconds (default 60s), so there can be a delay before pod creation starts.
- **File write race**: If two concurrent config POSTs hit different workers, the last write wins.
  This is acceptable for now; atomic file writes or a lock file can be added later if needed.

## Future Work

- Define proper Pydantic models in the SDK for config validation
- Consider adding a dedicated `GET /device-api/v1/edge/configure/status` endpoint
  to avoid URL construction gymnastics when polling
- Support reading current config via `GET /device-api/v1/edge/configure`
- Atomic file writes or lock file for concurrent config updates
