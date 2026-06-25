package alerting

import (
	"context"
	"fmt"
	"log"
)

type Severity string

const (
	SeverityInfo     Severity = "INFO"
	SeverityWarning  Severity = "WARNING"
	SeverityCritical Severity = "CRITICAL"
)

type Alert struct {
	Severity Severity
	Title    string
	Message  string
}

type Notifier interface {
	Notify(ctx context.Context, alert Alert) error
}

type LogNotifier struct{}

func (LogNotifier) Notify(ctx context.Context, alert Alert) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		log.Printf("[%s] %s: %s", alert.Severity, alert.Title, alert.Message)
		return nil
	}
}

func Critical(title string, format string, args ...any) Alert {
	return Alert{Severity: SeverityCritical, Title: title, Message: fmt.Sprintf(format, args...)}
}
