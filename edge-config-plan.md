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

## Implementation

### Edge Endpoint: `POST /device-api/v1/edge/configure`

**File**: `app/api/routes/edge_config.py`, registered in `app/api/api.py`

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

### End-to-End Flow

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

### Known Limitations

- **Multiprocess in-memory state**: Edge endpoint runs multiple uvicorn workers. The in-memory
  config update only applies to the worker that handles the POST. Other workers retain stale
  in-memory config until they restart. However, on restart they pick up the persisted runtime
  config from the PVC file.
- **Model updater refresh**: The model updater checks for new detectors every `refresh_rate`
  seconds (default 60s), so there can be a delay before pod creation starts.
- **File write race**: If two concurrent config POSTs hit different workers, the last write wins.
  This is acceptable for now; atomic file writes or a lock file can be added later if needed.

### Cloud vs. Edge Detection

| Scenario | What happens |
|---|---|
| SDK -> cloud (`api.groundlight.ai`) | Cloud returns 404 -> SDK raises error |
| SDK -> edge endpoint (with new route) | FastAPI handles it -> returns 200 |
| SDK -> old edge endpoint (without new route) | FastAPI returns 404 -> nginx falls back to cloud -> 404 -> SDK raises error |

## Future Work

- Define proper Pydantic models in the SDK for config validation
- Consider adding a dedicated `GET /device-api/v1/edge/configure/status` endpoint
  to avoid URL construction gymnastics when polling
- Support reading current config via `GET /device-api/v1/edge/configure`
- Atomic file writes or lock file for concurrent config updates
