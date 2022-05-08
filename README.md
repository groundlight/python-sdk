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

# Load the API client. This defaults to the prod endpoint, but you can specify a different
# endpoint like so: gl = Groundlight(endpoint="https://device.integ.positronix.ai/device-api")
gl = Groundlight()

# Call an API method (e.g., retrieve a list of detectors)
detectors = gl.list_detectors()

# You can access the fields, too! Your IDE should show type hints / autocomplete
# with these objects.
# See more details on the API docs (https://app.positronix.ai/reef/admin/api-docs).
print(f"Found {detectors.count} detectors!")
```

### What API methods are available?

Check out the [Examples](Examples.md)!

For more details, see the [Groundlight](src/groundlight/client.py) class. This SDK closely follows the methods in our [API Docs](https://app.positronix.ai/reef/admin/api-docs).

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

## Testing

Most tests need an API endpoint to run.

### Local API endpoint

1. Set up a local [janzu API endpoint](https://github.com/positronix-ai/zuuul/blob/main/deploy/README.md#development-using-local-microk8s) running (e.g., on an AWS GPU instance).

1. Set up an ssh tunnel to your laptop. That way, you can access the endpoint at http://localhost:8000/device-api (and the web UI at http://localhost:8000/reef):

    ```Bash
    $ ssh instance-name -L 8000:localhost:80
    ```

1. Run the tests (with an API token)

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    $ make test-local
    ```

(Note: in theory, it's possible to run the janzu API server on your laptop without microk8s - but some API methods don't work because of the dependence on GPUs)

### Integ API endpoint

1. Run the tests (with an API token)

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    $ make test-integ
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

- Figure out how we want to handle tests (since almost everything is an integration test). And, running the stateful (creation) tests can lead to a bunch of objects in the DB.
- Improve wrappers around API functions (e.g., simplify the responses even further, add auto-pagination managers, etc.)
  - The SDK should allow you to work with the most natural interface, rather than trying to exactly mirror the REST API.
  - E.g.
    - Add an image query long polling helper method (calls POST, then several GETs)
    - It would be nice to have a `get_or_create_detector()` function (even better if it's supported in the API directly). That way, "submit image query" code examples will be simpler.
- Better auto-generated code docs (e.g. [sphinx](https://www.sphinx-doc.org/en/master/))
  - Model types (e.g., [autodoc_pydantic](https://github.com/mansenfranzen/autodoc_pydantic))
- Better versioning strategy
- Better way of managing dependency on `public-ai.yaml` OpenAPI spec (right now, we just copy the file over manually)
- Update the web links (links to website, link to API endpoint, etc.)
- `with` context manager (auto cleanup the client object)
- ...
