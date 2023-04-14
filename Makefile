.PHONY: all test clean

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

test: install  ## Run tests against the prod API (needs GROUNDLIGHT_API_TOKEN)
	poetry run pytest -v --cov=src test

test-local: install  ## Run tests against a localhost API (needs GROUNDLIGHT_API_TOKEN and a local API server)
	GROUNDLIGHT_ENDPOINT="http://localhost:8000/" poetry run pytest -v --cov=src test

test-integ: install  ## Run tests against the integ API server (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_ENDPOINT="https://api.integ.groundlight.ai/" poetry run pytest --cov=src test --log-cli-level INFO

test-docs: install  ## Run the example code and tests in our docs against the prod API (needs GROUNDLIGHT_API_TOKEN)
	poetry run pytest --markdown-docs docs -v

lint: install-lint  ## Run linter to check formatting and style
	./code-quality/lint src test bin samples

format: install-lint  ## Run standard python formatting
	./code-quality/format src test bin samples
