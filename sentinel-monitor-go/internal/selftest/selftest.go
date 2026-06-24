package selftest

import (
	"context"
	"fmt"
	"time"
)

type Check interface {
	Name() string
	Run(ctx context.Context) error
}

type Result struct {
	OK       bool
	Sequence uint64
	Started  time.Time
	Ended    time.Time
	Errors   []string
}

type Runner struct {
	checks   []Check
	sequence uint64
}

func NewRunner(checks ...Check) *Runner {
	return &Runner{checks: checks}
}

func (r *Runner) Run(ctx context.Context) Result {
	r.sequence++
	result := Result{OK: true, Sequence: r.sequence, Started: time.Now().UTC()}
	for _, check := range r.checks {
		if err := check.Run(ctx); err != nil {
			result.OK = false
			result.Errors = append(result.Errors, fmt.Sprintf("%s: %v", check.Name(), err))
		}
	}
	result.Ended = time.Now().UTC()
	return result
}

type StaticCheck struct {
	CheckName string
	Err       error
}

func (s StaticCheck) Name() string { return s.CheckName }
func (s StaticCheck) Run(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	default:
		return s.Err
	}
}
