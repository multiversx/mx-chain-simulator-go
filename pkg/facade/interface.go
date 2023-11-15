package facade

// SimulatorHandler defines what a simulator handler should be able to do
type SimulatorHandler interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
