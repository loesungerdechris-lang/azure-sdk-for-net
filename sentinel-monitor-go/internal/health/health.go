package health

import (
	"encoding/json"
	"os"
	"time"
)

type Status struct {
	Service              string    `json:"service"`
	Healthy              bool      `json:"healthy"`
	LastSelfTestAt       time.Time `json:"last_self_test_at"`
	LastSelfTestSequence uint64    `json:"last_self_test_sequence"`
	Message              string    `json:"message"`
}

func Healthy(service string, sequence uint64, message string) Status {
	return Status{
		Service:              service,
		Healthy:              true,
		LastSelfTestAt:       time.Now().UTC(),
		LastSelfTestSequence: sequence,
		Message:              message,
	}
}

func Write(path string, status Status) error {
	payload, err := json.MarshalIndent(status, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(payload, '\n'), 0o600)
}
