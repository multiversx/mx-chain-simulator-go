FROM golang:1.20.7 AS builder


WORKDIR /multiversx
COPY mx-chain-go ./mx-chain-go
COPY mx-chain-simulator-go ./mx-chain-simulator-go

WORKDIR /multiversx/mx-chain-simulator-go
RUN go mod tidy

WORKDIR /multiversx/mx-chain-simulator-go/cmd/chainsimulator

RUN go build -o chainsimulator

RUN mkdir -p /lib_amd64 /lib_arm64

RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/mx-chain-simulator-go/go.sum | grep mx-chain-vm-v | sort -n | tail -n -1 | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer/libwasmer_linux_amd64.so /lib_amd64/
RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/mx-chain-simulator-go/go.sum | grep mx-chain-vm-go | sort -n | tail -n -1 | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer2/libvmexeccapi.so /lib_amd64/

RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/mx-chain-simulator-go/go.sum | grep mx-chain-vm-v | sort -n | tail -n -1 | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer/libwasmer_linux_arm64_shim.so /lib_arm64/
RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/mx-chain-simulator-go/go.sum | grep mx-chain-vm-go | sort -n | tail -n -1 | awk -F '/' '{print$3}' | sed 's/ /@/g')/wasmer2/libvmexeccapi_arm.so /lib_arm64/


FROM ubuntu:22.04
ARG TARGETARCH

RUN apt-get update && apt-get install -y git curl

COPY --from=builder /multiversx/mx-chain-simulator-go/cmd/chainsimulator /multiversx/mx-chain-simulator-go

EXPOSE 8085

WORKDIR /multiversx/mx-chain-simulator-go

# Copy architecture-specific files
COPY --from=builder "/lib_${TARGETARCH}/*" "/lib/"

CMD ["/bin/bash"]

ENTRYPOINT ["./chainsimulator"]
