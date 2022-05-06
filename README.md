# Groundlight Python SDK

This package holds an SDK for accessing the Groundlight public API. 

### Installation

The package is published to our [internal pypi repository](https://github.com/positronix-ai/packaging/tree/main/aws), so you can install it with tools like `pip` or `poetry`.

```Bash
# pip
$ pip install groundlight

# poetry
$ poetry add groundlight
```

### Basic Usage

To access the API, you need an API token. You can create one at [app.groundlight.ai](https://app.positronix.ai/reef/my-account/api-tokens). Then, add it as an environment variable called `GROUNDLIGHT_API_TOKEN`:

```Bash
$ export GROUNDLIGHT_API_TOKEN=tok_abc123
```

Now you can use the python SDK!

```Python
from groundlight import Groundlight

# Load the API client
gl = Groundlight()

# Call an API method (e.g., retrieve a list of detectors)
# The response will be an API response object
response = gl.list_detectors()

# You can extract the body data using .body - in this case, a paginated list of detectors.
detectors = response.body

# You can access the fields, too! Your IDE should show type hints / autocomplete
# with these objects.
# See more details on the API docs (https://app.positronix.ai/reef/admin/api-docs).
print(f"Found {detectors.count} detectors!")
```

### What API methods are available?

All the auto-generated methods are listed [here](generated/README.md#documentation-for-api-endpoints) - you can access these methods directly through the `Groundlight` API object. This SDK closely follows the methods in our [API Docs](https://app.positronix.ai/reef/admin/api-docs).

### Handling HTTP errors

If there is an HTTP error during an API call, it will raise an `ApiException`. You can access different metadata from that exception:

```Python
from groundlight import ApiException, Groundlight

gl = Groundlight()
try:
    detectors = gl.list_detectors()
except ApiException as e:
    print(e)
    print(e.args)
    print(e.body)
    print(e.headers)
    print(e.reason)
    print(e.status)
```

## Development

The auto-generated SDK code is in the `generated/` directory. To re-generate the client code, you'll need to install [openapi-generator](https://openapi-generator.tech/docs/installation#homebrew) (I recommend homebrew if you're on a mac). Then you can run it with:

```Bash
$ make generate
```

## Releases

To publish a new package version to our [internal pypi repository](https://github.com/positronix-ai/packaging/tree/main/aws), you create a release on github.

```Bash
# Create a git tag locally. Use semver "vX.Y.Z" format.
$ git tag -a v0.1.2 -m "Short description"

# Push the tag to the github repo
$ git push origin --tags
```

Then, go to the [github repo](https://github.com/positronix-ai/groundlight-python-sdk/tags) -> choose your tag -> create a release from this tag -> type in some description -> release. A [github action](https://github.com/positronix-ai/groundlight-python-sdk/actions/workflows/publish.yaml) will trigger a release, and then `groundlight-X.Y.Z` will be available for consumers.

## TODOs

- Tests
- Improve wrappers around API functions (e.g., so you don't have to call `.body` on a response, or add auto-pagination managers, etc.)
- `with` context manager
- Better auto-generated code docs
- Better versioning strategy
- Better way of managing dependency on OpenAPI spec (right now, we just copy the file over manually)
- Update the web links (links to website, link to API endpoint, etc.)
- Add an image query long polling helper method (calls POST, then several GETs)
- Add jpeg function helpers
- ...
