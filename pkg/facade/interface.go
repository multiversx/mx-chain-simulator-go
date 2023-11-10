package facade

type SimulatorHandler interface {
	GenerateBlocks(numOfBlocks int) error
	IsInterfaceNil() bool
}
