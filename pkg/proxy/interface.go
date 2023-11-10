package proxy

// ProxyHandler defines what a proxy handler should be able to do
type ProxyHandler interface {
	Close()
}
