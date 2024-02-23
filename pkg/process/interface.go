package process

// SimulatorHandler defines what a simulator handler should be able to do
type SimulatorHandler interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}

// BlocksGenerator defines a component able to generate blocks
type BlocksGenerator interface {
	Close()
}
