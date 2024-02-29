CHAIN_SIMULATOR_IMAGE_NAME=chainsimulator
CHAIN_SIMULATOR_IMAGE_TAG=latest
DOCKER_FILE=Dockerfile

docker-build:
	docker build \
		 -t ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG} \
		 -f ${DOCKER_FILE} \
		 .



IMAGE_NAME=simulator_image
run-faucet-test:
	$(MAKE) docker-build
	docker rm ${IMAGE_NAME} 2> /dev/null
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	sleep 2s
	cd examples/faucet && /bin/bash faucet.sh
	docker stop "${IMAGE_NAME}"

run-examples:
	$(MAKE) docker-build
	docker rm ${IMAGE_NAME} 2> /dev/null
	docker run -d --name "${IMAGE_NAME}" -p 8085:8085 ${CHAIN_SIMULATOR_IMAGE_NAME}:${CHAIN_SIMULATOR_IMAGE_TAG}
	cd scripts/run-examples && /bin/bash script.sh
	docker stop "${IMAGE_NAME}"
