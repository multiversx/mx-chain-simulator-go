package api

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/multiversx/mx-chain-go/node/chainSimulator/dtos"
	"github.com/multiversx/mx-chain-proxy-go/api/shared"
	"github.com/multiversx/mx-chain-proxy-go/data"
	dtosc "github.com/multiversx/mx-chain-simulator-go/pkg/dtos"
)

const (
	generateBlocksEndpoint            = "/simulator/generate-blocks/:num"
	generateBlockUnitEpochReached     = "/simulator/generate-blocks-until-epoch-reached/:epoch"
	initialWalletsEndpoint            = "/simulator/initial-wallets"
	setKeyValuesEndpoint              = "/simulator/address/:address/set-state"
	setStateMultipleEndpoint          = "/simulator/set-state"
	setStateMultipleOverwriteEndpoint = "/simulator/set-state-overwrite"
	addValidatorsKeys                 = "/simulator/add-keys"
	forceUpdateValidatorStatistics    = "/simulator/force-reset-validator-statistics"
	observersInfo                     = "/simulator/observers"
	epochChange                       = "/simulator/force-epoch-change"

	queryParamNoGenerate      = "noGenerate"
	queryParameterTargetEpoch = "targetEpoch"
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
	ws.POST(generateBlockUnitEpochReached, ep.generateBlocksUntilEpochReached)
	ws.GET(initialWalletsEndpoint, ep.initialWallets)
	ws.POST(setKeyValuesEndpoint, ep.setKeyValue)
	ws.POST(setStateMultipleEndpoint, ep.setStateMultiple)
	ws.POST(setStateMultipleOverwriteEndpoint, ep.setStateMultipleOverwrite)
	ws.POST(addValidatorsKeys, ep.addValidatorKeys)
	ws.POST(forceUpdateValidatorStatistics, ep.forceUpdateValidatorStatistics)
	ws.GET(observersInfo, ep.getObserversInfo)
	ws.POST(epochChange, ep.forceEpochChange)

	return nil
}

func (ep *endpointsProcessor) forceEpochChange(c *gin.Context) {
	targetEpoch, err := getTargetEpochQueryParam(c)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err = ep.facade.ForceChangeOfEpoch(uint32(targetEpoch))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func getTargetEpochQueryParam(c *gin.Context) (int, error) {
	epochStr := c.Request.URL.Query().Get(queryParameterTargetEpoch)
	if epochStr == "" {
		return 0, nil
	}

	epoch, err := strconv.Atoi(epochStr)
	if err != nil {
		shared.RespondWithBadRequest(c, "cannot convert string to number")
		return 0, errors.New("cannot convert string to number")
	}

	return epoch, nil
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

func (ep *endpointsProcessor) generateBlocksUntilEpochReached(c *gin.Context) {
	epochStr := c.Param("epoch")
	if epochStr == "" {
		shared.RespondWithBadRequest(c, "invalid epoch")
		return
	}

	epoch, err := strconv.Atoi(epochStr)
	if err != nil {
		shared.RespondWithBadRequest(c, "cannot convert string to number")
		return
	}

	err = ep.facade.GenerateBlocksUntilEpochIsReached(int32(epoch))
	if err != nil {
		shared.RespondWithInternalError(c, errors.New("cannot generate blocks"), err)
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) getObserversInfo(c *gin.Context) {
	observersData, err := ep.facade.GetObserversInfo()
	if err != nil {
		shared.RespondWithInternalError(c, errors.New("cannot get observers info"), err)
		return
	}

	shared.RespondWith(c, http.StatusOK, observersData, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) initialWallets(c *gin.Context) {
	initialWallets := ep.facade.GetInitialWalletKeys()

	shared.RespondWith(c, http.StatusOK, initialWallets, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) setKeyValue(c *gin.Context) {
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

	err = ep.facade.SetKeyValueForAddress(address, keyValueMap)
	if err != nil {
		shared.RespondWithInternalError(c, errors.New("cannot set key value pairs"), err)
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func getQueryParamNoGenerate(c *gin.Context) (bool, error) {
	withResultsStr := c.Request.URL.Query().Get(queryParamNoGenerate)
	if withResultsStr == "" {
		return false, nil
	}

	return strconv.ParseBool(withResultsStr)
}

func (ep *endpointsProcessor) setStateMultiple(c *gin.Context) {
	var stateSlice []*dtos.AddressState

	noGenerate, err := getQueryParamNoGenerate(c)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid query parameter %s, error: %s", queryParamNoGenerate, err.Error()))
		return
	}

	err = c.ShouldBindJSON(&stateSlice)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid state structure, error: %s", err.Error()))
		return
	}

	err = ep.facade.SetStateMultiple(stateSlice, noGenerate)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("cannot set state, error: %s", err.Error()))
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) setStateMultipleOverwrite(c *gin.Context) {
	noGenerate, err := getQueryParamNoGenerate(c)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid query parameter %s, error: %s", queryParamNoGenerate, err.Error()))
		return
	}

	var stateSlice []*dtos.AddressState
	err = c.ShouldBindJSON(&stateSlice)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid state structure, error: %s", err.Error()))
		return
	}

	err = ep.facade.SetStateMultipleOverwrite(stateSlice, noGenerate)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("cannot overwrite state, error: %s", err.Error()))
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) addValidatorKeys(c *gin.Context) {
	validatorsKeys := &dtosc.ValidatorKeys{}

	err := c.ShouldBindJSON(validatorsKeys)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("invalid validators keys structure, error: %s", err.Error()))
		return
	}

	err = ep.facade.AddValidatorKeys(validatorsKeys)
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("cannot add validator keys, error: %s", err.Error()))
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}

func (ep *endpointsProcessor) forceUpdateValidatorStatistics(c *gin.Context) {
	err := ep.facade.ForceUpdateValidatorStatistics()
	if err != nil {
		shared.RespondWithBadRequest(c, fmt.Sprintf("cannot force reset the validators statistics cache, error: %s", err.Error()))
		return
	}

	shared.RespondWith(c, http.StatusOK, gin.H{}, "", data.ReturnCodeSuccess)
}
