package testscommon

import (
	"github.com/multiversx/mx-chain-core-go/core"
	"github.com/multiversx/mx-chain-core-go/data"
	"github.com/multiversx/mx-chain-go/api/shared"
	"github.com/multiversx/mx-chain-go/consensus"
	"github.com/multiversx/mx-chain-go/factory"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	"github.com/multiversx/mx-chain-go/sharding"
)

// NodeHandlerStub -
type NodeHandlerStub struct {
	GetProcessComponentsCalled func() factory.ProcessComponentsHolder
}

// GetNetworkComponents -
func (n *NodeHandlerStub) GetNetworkComponents() factory.NetworkComponentsHolder {
	return nil
}

// GetBasePeers -
func (n *NodeHandlerStub) GetBasePeers() map[uint32]core.PeerID {
	return nil
}

// SetBasePeers -
func (n *NodeHandlerStub) SetBasePeers(_ map[uint32]core.PeerID) {
}

// GetProcessComponents -
func (n *NodeHandlerStub) GetProcessComponents() factory.ProcessComponentsHolder {
	if n.GetProcessComponentsCalled != nil {
		return n.GetProcessComponentsCalled()
	}

	return nil
}

// GetChainHandler -
func (n *NodeHandlerStub) GetChainHandler() data.ChainHandler {
	return nil
}

// GetBroadcastMessenger -
func (n *NodeHandlerStub) GetBroadcastMessenger() consensus.BroadcastMessenger {
	return nil
}

// GetShardCoordinator -
func (n *NodeHandlerStub) GetShardCoordinator() sharding.Coordinator {
	return nil
}

// GetCryptoComponents -
func (n *NodeHandlerStub) GetCryptoComponents() factory.CryptoComponentsHolder {
	return nil
}

// GetCoreComponents -
func (n *NodeHandlerStub) GetCoreComponents() factory.CoreComponentsHolder {
	return nil
}

// GetDataComponents -
func (n *NodeHandlerStub) GetDataComponents() factory.DataComponentsHolder {
	return nil
}

// GetStateComponents -
func (n *NodeHandlerStub) GetStateComponents() factory.StateComponentsHolder {
	return nil
}

// GetFacadeHandler -
func (n *NodeHandlerStub) GetFacadeHandler() shared.FacadeHandler {
	return nil
}

// GetStatusCoreComponents -
func (n *NodeHandlerStub) GetStatusCoreComponents() factory.StatusCoreComponentsHolder {
	return nil
}

// SetKeyValueForAddress -
func (n *NodeHandlerStub) SetKeyValueForAddress(_ []byte, _ map[string]string) error {
	return nil
}

// SetStateForAddress -
func (n *NodeHandlerStub) SetStateForAddress(_ []byte, _ *dtos.AddressState) error {
	return nil
}

// RemoveAccount -
func (n *NodeHandlerStub) RemoveAccount(_ []byte) error {
	return nil
}

// ForceChangeOfEpoch -
func (n *NodeHandlerStub) ForceChangeOfEpoch() error {
	return nil
}

// Close -
func (n *NodeHandlerStub) Close() error {
	return nil
}

// IsInterfaceNil -
func (n *NodeHandlerStub) IsInterfaceNil() bool {
	return n == nil
}
