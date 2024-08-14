# Python SDK Developer Guide

The raw API is generated using an [OpenAPI spec](spec/public-api.yaml). The SDK adds commonly used
functionality like polling for blocking submits and configuration of tokens and endpoints.

## Local Development

### Install dependencies

First, make sure you have [poetry installed](https://python-poetry.org/docs/#installation). Then,
you can install the package dependencies by running:

```shell
make install
```

Note: We support Python 3.8+ for clients of the SDK, but we recommend developing with Python 3.10+.

### Run tests

Most tests need an API endpoint and an API token to run. The default endpoint is the public API
endpoint (`https://api.groundlight.ai`). But you can also test against other endpoints (like
localhost or integ).

```shell
# Run tests against the public API
GROUNDLIGHT_API_TOKEN="api_YOUR_PROD_TOKEN_HERE" make test
```

But you can also test against other endpoints (like localhost or integ). Make sure the API token
comes from the same environment as the API endpoint you're testing against!

```shell
# Run tests against a local API
GROUNDLIGHT_API_TOKEN="api_YOUR_LOCALHOST_TOKEN_HERE" make test-local

# Run tests against the integ API
GROUNDLIGHT_API_TOKEN="api_YOUR_INTEG_TOKEN_HERE" make test-integ
```

### Install auto-formatter pre-commit hook

We use [pre-commit](https://pre-commit.com/) to run some auto-formatters before committing code. You
can install the pre-commit hooks by running:

```shell
make install-pre-commit
```

This will check to see whether any formatters need to be run every time you do `git commit`. If so,
it will run them, add the changes, and then ask you to try committing again with the new changes.

### Generating code based on the latest API spec

The auto-generated SDK code is in the [generated/](generated) directory. Most of the time, you won't
need to generate code. But if the API specification changes, you may need to generate SDK code. To
re-generate the client code, you'll need to [install npm](https://github.com/nvm-sh/nvm#intro)
first. Then you can install the code generator by running:

```shell
make install-generator
```

Then you can generate the code by running:

```shell
make generate
```

### Linters

Linters help us find issues before runtime. We're currently using:

- [ruff](https://beta.ruff.rs/docs/) and
  [pylint](https://pylint.readthedocs.io/en/latest/index.html) for general python linting.
- [mypy](https://mypy.readthedocs.io/en/stable/index.html) for type checking.
- [black](https://black.readthedocs.io/en/stable/index.html) for standardizing code formatting.
- [toml-sort](https://toml-sort.readthedocs.io/en/latest/) for linting the `pyproject.toml` file.

Most of these linters are configured in [pyproject.toml](pyproject.toml) (except for `pylint` in
[.pylintrc](.pylintrc)). Sometimes the linters are wrong or not useful, so we can add overrides. We
prefer to make the smallest possible override:

- single line override with a specific rule (e.g., `# pylint: disable=some-rule` or `# ruff: noqa: F403`)
- single file override with a specific rule
- single file override with a whole class of rules
- global override for a specific rule

Note: `pylint` is usually the strictest and slowest, so we may end up turning it off - but we'll try
it for a while and see how it goes!
