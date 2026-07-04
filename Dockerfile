# ---------------------------------------------------------------------------
# Stage 1: Fetch configs
# ---------------------------------------------------------------------------
FROM --platform=$BUILDPLATFORM golang:1.23.6-bookworm AS config-fetcher

WORKDIR /src
COPY . .

WORKDIR /src/cmd/chainsimulator
RUN go build -o chainsimulator \
    && ./chainsimulator --fetch-configs-and-close

# ---------------------------------------------------------------------------
# Stage 2: Build the binary + extract Wasmer libs
# ---------------------------------------------------------------------------
FROM golang:1.23.6-bookworm AS builder

WORKDIR /src
COPY . .

# Download all modules
RUN go mod download

WORKDIR /src/cmd/chainsimulator

# Build with optimizations: strip debug symbols, smaller binary
# CGO_ENABLED=1 is implicit and required by Wasmer bindings.
RUN go build \
    -ldflags="-s -w" \
    -trimpath \
    -o /out/chainsimulator

# ---------------------------------------------------------------------------
# Extract architecture-specific Wasmer shared libraries
# ---------------------------------------------------------------------------
RUN mkdir -p /out/lib

RUN cp /go/pkg/mod/github.com/multiversx/$(cat /src/go.sum \
    | grep mx-chain-vm-v | sort -n | tail -n -1 \
    | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer/libwasmer_linux_$(dpkg --print-architecture | sed 's/arm64/arm64_shim/').so \
    /out/lib/ 2>/dev/null || true

RUN cp /go/pkg/mod/github.com/multiversx/$(cat /src/go.sum \
    | grep mx-chain-vm-go | sort -n | tail -n -1 \
    | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer2/libvmexeccapi$(dpkg --print-architecture | sed 's/amd64//;s/arm64/_arm/').so \
    /out/lib/ 2>/dev/null || true

# ---------------------------------------------------------------------------
# Stage 3: Minimal runtime image (distroless)
# ---------------------------------------------------------------------------
FROM gcr.io/distroless/cc-debian13:nonroot

LABEL org.opencontainers.image.title="mx-chain-simulator-go" \
    org.opencontainers.image.description="MultiversX Chain Simulator" \
    org.opencontainers.image.source="https://github.com/multiversx/mx-chain-simulator-go" \
    org.opencontainers.image.licenses="GPL-3.0"

# Copy binary
COPY --from=builder --chown=nonroot:nonroot /out/chainsimulator /app/chainsimulator

# Copy pre-fetched configs
COPY --from=config-fetcher --chown=nonroot:nonroot /src/cmd/chainsimulator/config /app/config

# Copy Wasmer libs
COPY --from=builder /out/lib/ /lib/

WORKDIR /app
EXPOSE 8085

# Run as non-root for security (UID 65532 is "nonroot" in distroless)
USER nonroot:nonroot

ENTRYPOINT ["./chainsimulator"]
