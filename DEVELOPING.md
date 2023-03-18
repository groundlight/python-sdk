# Python SDK Developer Guide

The raw API is generated using an OpenAPI spec.  The SDK adds commonly used functionality
like polling for blocking submits and configuration of tokens and endpoints.

## Local Development

The auto-generated SDK code is in the `generated/` directory. To
re-generate the client code, you'll need to install
[openapi-generator](https://openapi-generator.tech/docs/installation#homebrew)
(I recommend homebrew if you're on a mac). Then you can run it with:

```Bash
$ make generate
```

## Testing
Most tests need an API endpoint to run.  This can be the public API endpoint `https://api.groundlight.ai`,
or a local endpoint with an edge client or development environment.

### Getting the tests to use your current code.

(This needs to be updated.)

You kinda want to do a `pip install -e .` equivalent but I don't know how to do that with poetry.  The ugly version is this...

Find the directory where `groundlight` is installed:

```
$  python
Python 3.7.4 (default, Aug 13 2019, 20:35:49)
[GCC 7.3.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import groundlight
>>> groundlight
<module 'groundlight' from '/home/ubuntu/anaconda3/lib/python3.7/site-packages/groundlight/__init__.py'>
```

Then blow this away and set up a symlink from that directory to your source.

```
cd /home/ubuntu/anaconda3/lib/python3.7/site-packages/
rm -rf groundlight
ln -s ~/dev/python-sdk/src/groundlight groundlight
```
