package facade

import "errors"

var (
	errNilSimulatorHandler         = errors.New("nil simulator handler ")
	errInvalidNumOfBlocks          = errors.New("num of blocks must be greater than zero")
	errNilProxyTransactionsHandler = errors.New("nil proxy transactions handler ")
)
