package api

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/multiversx/mx-chain-proxy-go/api/shared"
	"github.com/multiversx/mx-chain-proxy-go/data"
)

const (
	generateBlocksEndpoint = "/simulator/generate-blocks/:num"
	initialWalletsEndpoint = "/simulator/initial-wallets"
	setKeyValuesEndpoint   = "/simulator/:address/set-state"
)

type endpointsProcessor struct {
	facade SimulatorFacade
}

// NewEndpointsProcessor will create a new instance of endpointsProcessor
func NewEndpointsProcessor(facade SimulatorFacade) (*endpointsProcessor, error) {
	return &endpointsProcessor{
		facade: facade,
	}, nil
}

// ExtendProxyServer will extend the proxy server with extra endpoints
func (ep *endpointsProcessor) ExtendProxyServer(httpServer *http.Server) error {
	ws, ok := httpServer.Handler.(*gin.Engine)
	if !ok {
		return errors.New("cannot cast httpServer.Handler to gin.Engine")
	}

	ws.POST(generateBlocksEndpoint, ep.generateBlocks)
	ws.GET(initialWalletsEndpoint, ep.initialWallets)
	ws.POST(setKeyValuesEndpoint, ep.setState)

	return nil
}

func (ep *endpointsProcessor) generateBlocks(c *gin.Context) {
	numStr := c.Param("num")
	if numStr == "" {
		shared.RespondWithBadRequest(c, "invalid number of blocks")
		return
	}

	num, err := strconv.Atoi(numStr)
	if err != nil {
		shared.RespondWithBadRequest(c, "cannot convert string to number")
		return
	}

	err = ep.facade.GenerateBlocks(num)
	if err != nil {
		shared.RespondWithInternalError(c, errors.New("cannot generate blocks"), err)
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) initialWallets(c *gin.Context) {
	initialWallets := ep.facade.GetInitialWalletKeys()

	shared.RespondWith(c, http.StatusOK, initialWallets, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) setState(c *gin.Context) {
	address := c.Param("address")
	if address == "" {
		shared.RespondWithBadRequest(c, "invalid provided address")
		return
	}

	var keyValueMap = map[string]string{}
	err := c.ShouldBindJSON(&keyValueMap)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid key value map, error: %s", err.Error()))
		return
	}

	err = ep.facade.SetState(address, keyValueMap)
	if err != nil {
		shared.RespondWithInternalError(c, errors.New("cannot set state"), err)
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}
