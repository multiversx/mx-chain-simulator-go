package disabled

type blocksGenerator struct {
}

// NewBlocksGenerator returns a new instance of disabled blocks generator
func NewBlocksGenerator() *blocksGenerator {
	return &blocksGenerator{}
}

// Close does nothing as it is disabled
func (generator *blocksGenerator) Close() {
}
