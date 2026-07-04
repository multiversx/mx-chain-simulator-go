IMAGE_NAME       ?= chainsimulator
IMAGE_TAG        ?= latest
REGISTRY         ?= multiversx
DOCKER_FILE      ?= Dockerfile
PLATFORMS        ?= linux/amd64,linux/arm64
CONTAINER_NAME   ?= simulator_instance
FULL_IMAGE       = $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

## Build the Go binary locally
.PHONY: build
build:
	cd cmd/chainsimulator && go build -ldflags="-s -w" -trimpath -o chainsimulator

## Fetch configs locally
.PHONY: fetch-configs
fetch-configs: build
	cd cmd/chainsimulator && ./chainsimulator --fetch-configs-and-close

## Build Docker image (single arch, current platform)
.PHONY: docker-build
docker-build:
	DOCKER_BUILDKIT=1 docker build \
		-t $(FULL_IMAGE) \
		-f $(DOCKER_FILE) \
		.

## Build multi-arch image and push to registry (requires login)
## This is the correct way to produce a multi-platform manifest.
.PHONY: docker-build-push
docker-build-push:
	docker buildx build \
		--platform $(PLATFORMS) \
		-t $(FULL_IMAGE) \
		-f $(DOCKER_FILE) \
		--push \
		.

## Register QEMU for cross-platform builds (run once per boot)
.PHONY: qemu-setup
qemu-setup:
	docker run --rm --privileged multiarch/qemu-user-static --reset -p yes

## Run the simulator container
.PHONY: docker-run
docker-run:
	docker run -d \
		--name "$(CONTAINER_NAME)" \
		--read-only \
		--tmpfs /tmp \
		-p 8085:8085 \
		$(FULL_IMAGE)

## Stop and remove the simulator container
.PHONY: docker-stop
docker-stop:
	docker stop "$(CONTAINER_NAME)" 2>/dev/null || true
	docker rm "$(CONTAINER_NAME)" 2>/dev/null || true

## Run faucet example test
.PHONY: run-faucet-test
run-faucet-test: docker-build
	docker run -d --name "$(CONTAINER_NAME)" -p 8085:8085 $(FULL_IMAGE)
	sleep 2s
	cd examples/faucet && /bin/bash faucet.sh
	$(MAKE) docker-stop

## Run all examples
.PHONY: run-examples
run-examples:
	printf '%s\n' '{ File = "enableEpochs.toml", Path = "EnableEpochs.StakeLimitsEnableEpoch", Value = 1000000 },' > temp.txt
	sed -i '4r temp.txt' cmd/chainsimulator/config/nodeOverrideDefault.toml
	rm temp.txt
	$(MAKE) docker-build
	docker run -d --name "$(CONTAINER_NAME)" -p 8085:8085 $(FULL_IMAGE)
	cd scripts/run-examples && /bin/bash install-python-deps.sh && /bin/bash script.sh
	$(MAKE) docker-stop

## Install golint if not already present
.PHONY: lint-install
lint-install:
ifeq (,$(wildcard test -f bin/golangci-lint))
	@echo "Installing golint"
	curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s
endif

## Run golint on the codebase
.PHONY: run-lint
run-lint:
	@echo "Running golint"
	bin/golangci-lint run --max-issues-per-linter 0 --max-same-issues 0 --timeout=2m

## Run lint installation and then the linter
.PHONY: lint
lint: lint-install run-lint

## Show image details
.PHONY: docker-info
docker-info:
	@echo "Image:      $(FULL_IMAGE)"
	@echo "Dockerfile: $(DOCKER_FILE)"
	@echo "Platforms:  $(PLATFORMS)"
	@docker images $(FULL_IMAGE) --format "Size: {{.Size}}"

## Run security scan with trivy (if installed)
.PHONY: docker-scan
docker-scan:
	trivy image --severity HIGH,CRITICAL $(FULL_IMAGE)

## Show available targets
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  build              Build Go binary locally"
	@echo "  fetch-configs      Fetch configs from GitHub repos"
	@echo "  docker-build       Build Docker image (current platform, docker build)"
	@echo "  docker-build-push  Build & push multi-arch image to registry"
	@echo "  qemu-setup         Register QEMU for cross-arch builds"
	@echo "  docker-run         Run the simulator container (read-only)"
	@echo "  docker-stop        Stop and remove container"
	@echo "  docker-info        Show image details"
	@echo "  docker-scan        Trivy security scan"
	@echo "  lint               Run linter"
	@echo "  help               Show this help"
