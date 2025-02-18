CHAIN_SIMULATOR_IMAGE_NAME=chainsimulator
CHAIN_SIMULATOR_IMAGE_TAG=latest
DOCKER_FILE=Dockerfile
IMAGE_NAME=simulator_image

docker-build:
	sudo docker build \
		 -t ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} \
		 -f ${DOCKER_FILE} \
		 .

run-faucet-test:
	$(MAKE) docker-build
	sudo docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	sleep 2s
	cd examples/faucet && /bin/bash faucet.sh
	sudo docker stop "${IMAGE_NAME}"
	sudo docker rm ${IMAGE_NAME} 2> /dev/null

run-examples:
	$(MAKE) docker-build
	sudo docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	cd scripts/run-examples && /bin/bash script.sh
	sudo docker stop "${IMAGE_NAME}"
	sudo docker rm ${IMAGE_NAME}

lint-install:
ifeq (,$(wildcard test -f bin/golangci-lint))
	@echo "Installing golint"
	curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s
endif

run-lint:
	@echo "Running golint"
	bin/golangci-lint run --max-issues-per-linter 0 --max-same-issues 0 --timeout=2m

lint: lint-install run-lint
