package api

// SimulatorFacade defines what a simulator facade should be able to do
type SimulatorFacade interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
