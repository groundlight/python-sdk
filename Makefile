.PHONY: all test clean

install:  ## Install the package from source
	poetry install

# Java weirdness - see https://github.com/OpenAPITools/openapi-generator/issues/11763#issuecomment-1098337960
generate: install  ## Generate the SDK from our public openapi spec
	_JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED \
	--add-opens=java.base/java.util=ALL-UNNAMED" \
		openapi-generator generate -i spec/public-api.yaml \
		-g python \
		-o ./generated
	poetry run datamodel-codegen  --input spec/public-api.yaml --output generated/model.py

test-local: install  ## Run integration tests against an API server running at http://localhost:8000/device-api (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_TEST_API_ENDPOINT="http://localhost:8000/device-api" poetry run pytest --cov=src test --log-cli-level INFO


test-integ: install  ## Run integration tests against the integ API server (needs GROUNDLIGHT_API_TOKEN)
	GROUNDLIGHT_TEST_API_ENDPOINT="https://device.integ.positronix.ai/device-api" poetry run pytest --cov=src test --log-cli-level INFO
