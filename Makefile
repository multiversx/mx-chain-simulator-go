CHAIN_SIMULATOR_IMAGE_NAME=chainsimulator
CHAIN_SIMULATOR_IMAGE_TAG=latest
DOCKER_FILE=Dockerfile
SOVEREIGN_DOCKER_FILE=Dockerfile-sovereign
IMAGE_NAME=simulator_image

docker-build:
	docker build \
		 -t ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} \
		 -f ${DOCKER_FILE} \
		 .

docker-sovereign-build:
	cd .. && docker build \
		 -t ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} \
		 -f mx-chain-simulator-go/${SOVEREIGN_DOCKER_FILE} \
		 .

run-faucet-test:
	$(MAKE) ${BUILD}
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	sleep 2s
	cd examples/faucet && /bin/bash faucet.sh
	docker stop "${IMAGE_NAME}"
	docker rm ${IMAGE_NAME} 2> /dev/null

run-examples:
	printf '%s\n' '{ File = "enableEpochs.toml", Path = "EnableEpochs.StakeLimitsEnableEpoch", Value = 1000000 },' > temp.txt
	sed -i '4r temp.txt' cmd/chainsimulator/config/nodeOverrideDefault.toml
	rm temp.txt

	$(MAKE) ${BUILD}
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	cd scripts/run-examples && /bin/bash script.sh
	docker stop "${IMAGE_NAME}"
	docker rm ${IMAGE_NAME}

lint-install:
ifeq (,$(wildcard test -f bin/golangci-lint))
	@echo "Installing golint"
	curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s
endif

run-lint:
	@echo "Running golint"
	bin/golangci-lint run --max-issues-per-linter 0 --max-same-issues 0 --timeout=2m

lint: lint-install run-lint
