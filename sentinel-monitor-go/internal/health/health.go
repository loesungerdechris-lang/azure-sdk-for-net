package health

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
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
	return Status{Service: service, Healthy: true, LastSelfTestAt: time.Now().UTC(), LastSelfTestSequence: sequence, Message: message}
}

func Failed(service string, sequence uint64, message string) Status {
	return Status{Service: service, Healthy: false, LastSelfTestAt: time.Now().UTC(), LastSelfTestSequence: sequence, Message: message}
}

func Write(path string, status Status) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	payload, err := json.MarshalIndent(status, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(payload, '\n'), 0o600)
}

func CheckFile(path string, maxAge time.Duration) error {
	payload, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("read health file: %w", err)
	}
	var status Status
	if err := json.Unmarshal(payload, &status); err != nil {
		return fmt.Errorf("parse health file: %w", err)
	}
	if !status.Healthy {
		return fmt.Errorf("service reports failed status: %s", status.Message)
	}
	if time.Since(status.LastSelfTestAt) > maxAge {
		return fmt.Errorf("health status is stale")
	}
	return nil
}
