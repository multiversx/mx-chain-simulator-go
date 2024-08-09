FROM golang:1.20.7 as builder


WORKDIR /multiversx
COPY . .

RUN go mod tidy

WORKDIR /multiversx/cmd/chainsimulator

RUN go build -o chainsimulator

RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/go.sum | grep mx-chain-vm-v | sort -n | tail -n -1| awk -F '/' '{print$3}'| sed 's/ /@/g')/wasmer/libwasmer_linux_amd64.so /lib/libwasmer_linux_amd64.so
RUN cp /go/pkg/mod/github.com/multiversx/$(cat /multiversx/go.sum | grep mx-chain-vm-go | sort -n | tail -n -1| awk -F '/' '{print$3}'| sed 's/ /@/g')/wasmer2/libvmexeccapi.so /lib/libvmexeccapi.so


FROM ubuntu:22.04

RUN apt-get update \
    && apt-get -y install git \
    && apt-get clean

COPY --from=builder /multiversx/cmd/chainsimulator /multiversx

EXPOSE 8085

WORKDIR /multiversx

COPY --from=builder "/lib/libwasmer_linux_amd64.so" "/lib/libwasmer_linux_amd64.so"
COPY --from=builder "/lib/libvmexeccapi.so" "/lib/libvmexeccapi.so"

RUN apt-get update && apt-get install -y curl
CMD /bin/bash

ENTRYPOINT ["./chainsimulator"]


