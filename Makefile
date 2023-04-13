.PHONY: all test clean

install:  ## Install the package from source
	poetry install

install-lint:  ## Only install the linter dependencies
	poetry install --only lint

install-pre-commit: install  ## Install pre-commit hooks
	poetry run pre-commit install

generate: install  ## Generate the SDK from our public openapi spec
	node_modules/.bin/openapi-generator-cli generate -i spec/public-api.yaml \
		-g python \
		-o ./generated
	poetry run datamodel-codegen  --input spec/public-api.yaml --output generated/model.py
	poetry run black .

test-local: install  ## Run integration tests against an API server running at http://localhost:8000/device-api (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_ENDPOINT="http://localhost:8000/" poetry run pytest --cov=src test --log-cli-level INFO

test-integ: install  ## Run integration tests against the integ API server (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_ENDPOINT="https://api.integ.groundlight.ai/" poetry run pytest --cov=src test --log-cli-level INFO

test-docs: install  ## Run the example code and tests in our docs against the prod API (needs GROUNDLIGHT_API_TOKEN)
	poetry run pytest --markdown-docs docs -v

lint: install-lint  ## Run linter to check formatting and style
	./code-quality/lint src test bin

format: install-lint  ## Run standard python formatting
	./code-quality/format src test bin
