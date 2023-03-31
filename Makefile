.PHONY: all test clean

install:  ## Install the package from source
	poetry install
	npm install

generate: install  ## Generate the SDK from our public openapi spec
	node_modules/.bin/openapi-generator-cli generate -i spec/public-api.yaml \
		-g python \
		-o ./generated
	poetry run datamodel-codegen  --input spec/public-api.yaml --output generated/model.py
	poetry run black .


test-local: install  ## Run integration tests against an API server running at http://localhost:8000/device-api (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_API_ENDPOINT="http://localhost:8000/" poetry run pytest --cov=src test --log-cli-level INFO


test-integ: install  ## Run integration tests against the integ API server (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_API_ENDPOINT="https://api.integ.groundlight.ai/" poetry run pytest --cov=src test --log-cli-level INFO
