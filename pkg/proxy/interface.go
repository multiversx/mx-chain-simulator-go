package proxy

import "net/http"

// ProxyHandler defines what a proxy handler should be able to do
type ProxyHandler interface {
	Start()
	GetHttpServer() *http.Server
	Close()
}
