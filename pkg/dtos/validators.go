package dtos

// ValidatorsKeys is the dto for the validators private key structure
type ValidatorsKeys struct {
	PrivateKeysBase64 []string `json:"privateKeysBase64"`
}
