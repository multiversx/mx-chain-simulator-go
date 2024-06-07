package testscommon

import "github.com/multiversx/mx-chain-proxy-go/data"

// TransactionHandlerMock -
type TransactionHandlerMock struct {
	GetProcessedTransactionStatusCalled func(txHash string) (*data.ProcessStatusResponse, error)
}

// GetProcessedTransactionStatus -
func (th *TransactionHandlerMock) GetProcessedTransactionStatus(txHash string) (*data.ProcessStatusResponse, error) {
	if th.GetProcessedTransactionStatusCalled != nil {
		return th.GetProcessedTransactionStatusCalled(txHash)
	}

	return nil, nil
}
