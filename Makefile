CHAIN_SIMULATOR_IMAGE_NAME=chainsimulator
CHAIN_SIMULATOR_IMAGE_TAG=latest
DOCKER_FILE=Dockerfile
IMAGE_NAME=simulator_image

sovereign-build:
	./scripts/prerequisites-sovereign.sh

	cd ../mx-chain-simulator-go && \
	go mod tidy && \
	cd cmd/chainsimulator && \
	go build

docker-build:
	cd .. && docker build \
		 -t ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} \
		 -f mx-chain-simulator-go/${DOCKER_FILE} \
		 .

run-faucet-test:
	$(MAKE) docker-build
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} ${SIMULATOR_TYPE}
	sleep 2s
	cd examples/faucet && /bin/bash faucet.sh
	docker stop "${IMAGE_NAME}"
	docker rm ${IMAGE_NAME} 2> /dev/null

run-examples:
	printf '%s\n' '{ File = "enableEpochs.toml", Path = "EnableEpochs.StakeLimitsEnableEpoch", Value = 1000000 },' > temp.txt
	sed -i '4r temp.txt' cmd/chainsimulator/config/nodeOverrideDefault.toml
	rm temp.txt

	$(MAKE) docker-build
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} ${SIMULATOR_TYPE}
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
