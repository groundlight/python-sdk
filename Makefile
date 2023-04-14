install:  ## Install the package from source
	poetry install

install-lint:  ## Only install the linter dependencies
	poetry install --only lint

install-pre-commit: install  ## Install pre-commit hooks
	poetry run pre-commit install

install-generator: install ## Install dependencies for SDK code generator
	npm install

generate: install-generator  ## Generate the SDK from our public openapi spec
	node_modules/.bin/openapi-generator-cli generate -i spec/public-api.yaml \
		-g python \
		-o ./generated
	poetry run datamodel-codegen  --input spec/public-api.yaml --output generated/model.py
	poetry run black .

PYTEST=poetry run pytest -v --cov=src

# You can pass extra arguments to pytest by setting the TEST_ARGS environment variable.
# For example:
# 	`make test TEST_ARGS="-k some_filter"`
TEST_ARGS=

test: install  ## Run tests against the prod API (needs GROUNDLIGHT_API_TOKEN)
	${PYTEST} ${TEST_ARGS} test

test-local: install  ## Run tests against a localhost API (needs GROUNDLIGHT_API_TOKEN and a local API server)
	GROUNDLIGHT_ENDPOINT="http://localhost:8000/" ${PYTEST} ${TEST_ARGS} test

test-integ: install  ## Run tests against the integ API server (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_ENDPOINT="https://api.integ.groundlight.ai/" ${PYTEST} ${TEST_ARGS} test

test-docs: install  ## Run the example code and tests in our docs against the prod API (needs GROUNDLIGHT_API_TOKEN)
	poetry run pytest -v --markdown-docs ${TEST_ARGS} docs

# Adjust which paths we lint
LINT_PATHS="src test bin samples"

lint: install-lint  ## Run linter to check formatting and style
	./code-quality/lint ${LINT_PATHS}

format: install-lint  ## Run standard python formatting
	./code-quality/format ${LINT_PATHS}
