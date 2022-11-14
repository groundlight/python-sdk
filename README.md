# Python SDK Internal README
# (See [UserGuide](UserGuide.md) for the public README)

This package builds the SDK which is an easier-to-use wrapper around the public API.  
The raw API is generated using an OpenAPI spec.  But then we add functionality here in the SDK
for things like blocking submit and configuration of tokens and endpoints.

The SDK is published through github actions to pypi at [https://pypi.org/project/groundlight/](https://pypi.org/project/groundlight/).

### Usage

For instructions on using the SDK see the public [User Guide](UserGuide.md).

For more details, see the [Groundlight](src/groundlight/client.py)
class. This SDK closely follows the methods in our [API 
Docs](https://app.groundlight.ai/reef/admin/public-api-docs/).

## Development

The auto-generated SDK code is in the `generated/` directory. To
re-generate the client code, you'll need to install
[openapi-generator](https://openapi-generator.tech/docs/installation#homebrew)
(I recommend homebrew if you're on a mac). Then you can run it with:

```Bash
$ make generate
```

## Testing
Most tests need an API endpoint to run.

### Getting the tests to use your current code.

You kinda want to do a `pip install -e .` equivalent but I don't know how to do that with poetry.  The ugly version is this...

Find the directory where `groundlight` is installed:

```
$  python
Python 3.7.4 (default, Aug 13 2019, 20:35:49)
[GCC 7.3.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import groundlight
>>> groundlight
<module 'groundlight' from '/home/leo/anaconda3/lib/python3.7/site-packages/groundlight/__init__.py'>
```

Then blow this away and set up a symlink from that directory to your source.

```
cd /home/leo/anaconda3/lib/python3.7/site-packages/
rm -rf groundlight
ln -s ~/ptdev/groundlight-python-sdk/src/groundlight groundlight
```

TODO: something better.

### Local API endpoint

1. Set up a local [janzu API
   endpoint](https://github.com/positronix-ai/zuuul/blob/main/deploy/README.md#development-using-local-microk8s)
   running (e.g., on an AWS GPU instance).

1. Set up an ssh tunnel to your laptop. That way, you can access the
   endpoint at http://localhost:8000/device-api (and the web UI at
   http://localhost:8000/reef):

    ```Bash
    $ ssh instance-name -L 8000:localhost:80
    ```

1. Run the tests (with an API token)

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    $ make test-local
    ```

(Note: in theory, it's possible to run the janzu API server on your
laptop without microk8s - but some API methods don't work because of
the dependence on GPUs)

### Integ API endpoint

1. Run the tests (with an API token)

    ```Bash
    $ export GROUNDLIGHT_API_TOKEN=tok_abc123
    $ make test-integ
    ```

## Releases

To publish a new package version to our [internal pypi
repository](https://github.com/positronix-ai/packaging/tree/main/aws),
you create a release on github.

```Bash
# Create a git tag locally. Use semver "vX.Y.Z" format.
$ git tag -a v0.1.2 -m "Short description"

# Push the tag to the github repo
$ git push origin --tags
```

Then, go to the [github
repo](https://github.com/positronix-ai/groundlight-python-sdk/tags) ->
choose your tag -> create a release from this tag -> type in some
description -> release. A [github
action](https://github.com/positronix-ai/groundlight-python-sdk/actions/workflows/publish.yaml)
will trigger a release, and then `groundlight-X.Y.Z` will be available
for consumers.

## TODOs

- Improve wrappers around API functions (e.g., simplify the responses even further, add auto-pagination managers, etc.)
  - The SDK should allow you to work with the most natural interface, rather than trying to exactly mirror the REST API.
- Better auto-generated code docs (e.g. [sphinx](https://www.sphinx-doc.org/en/master/))
  - Model types (e.g., [autodoc_pydantic](https://github.com/mansenfranzen/autodoc_pydantic))
  - Cleaner auto-generated model names (e.g., `PaginatedDetectorList` is a little ugly)
- Better versioning strategy. On the one hand, this package will closely follow the versioning in the HTTP API. On the other hand, we may add features in the client (like image utils, shortcuts, etc.) that are not in the REST API.
- Better way of managing dependency on `public-api.yaml` OpenAPI spec (right now, we just copy the file over manually)
- Update the web links (links to website, link to API endpoint, etc.)
- `with` context manager (auto cleanup the client object)
- It would be great to add notebooks with interactive examples that can actually run out of the box
- Have a cleaner distinction between dev docs and user guide docs
