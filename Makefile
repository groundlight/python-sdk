# Java weirdness - see https://github.com/OpenAPITools/openapi-generator/issues/11763#issuecomment-1098337960
generate:  ## Generate the SDK from our public openapi spec
	_JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED \
	--add-opens=java.base/java.util=ALL-UNNAMED" \
		openapi-generator generate -i spec/public-api.yaml \
		-g python-experimental \
		-o ./generated
