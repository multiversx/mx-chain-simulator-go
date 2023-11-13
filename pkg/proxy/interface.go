package proxy

// ProxyHandler defines what a proxy handler should be able to do
type ProxyHandler interface {
	Start()
	Close()
}

// SimulatorFacade defines what a simulator facade should be able to do
type SimulatorFacade interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
