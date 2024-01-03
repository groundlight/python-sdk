# Documentation: code.groundlight.ai

This part of the SDK repo contains all the code for the website at [code.groundlight.ai](https://code.groundlight.ai/)  It is built with [Docusaurus 2](https://docusaurus.io/).

The docs are included with the SDK so that we can automate testing of the code samples in the documentation.  This way we can ensure that the code samples in our docs always work with the current SDK.

## Previewing doc changes

Doc changes are published automatically when they're merged to main.  To preview changes, build and host the site locally.  You'll need a reasonably modern version of `npm` and then:

```
cd docs 
npm install 
cd .. 
make develop-docs-comprehensive
```

and then open [http://localhost:3000/python-sdk](http://localhost:3000/python-sdk).

Or if you're feeling luck, you can try `./start_docs_server.sh` which also rebuilds the sphinx docs on every change.
This script is tested on MacOS with [homebrew](https://brew.sh/) installed, but could work elsewhere too.

## Running docs tests

You'll need `python poetry` and `make` installed.  And you'll need an API Token configured.  Then you can just run:

```
make test-docs
```

