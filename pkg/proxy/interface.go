package proxy

// ProxyHandler defines what a proxy handler should be able to do
type ProxyHandler interface {
	Start()
	Close()
}

type SimulatorFacade interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
