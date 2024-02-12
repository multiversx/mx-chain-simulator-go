package dtos

// ValidatorKeys is the dto for the validators private key structure
type ValidatorKeys struct {
	PrivateKeysBase64 []string `json:"privateKeysBase64"`
}
