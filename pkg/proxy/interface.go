package proxy

import (
	"github.com/multiversx/mx-chain-proxy-go/data"
	"net/http"
)

// ProxyHandler defines what a proxy handler should be able to do
type ProxyHandler interface {
	Start()
	GetHttpServer() *http.Server
	Close()
}

// ProxyTransactionsHandler defines what a proxy transaction handler should be able to do
type ProxyTransactionsHandler interface {
	GetProcessedTransactionStatus(txHash string) (*data.ProcessStatusResponse, error)
}
