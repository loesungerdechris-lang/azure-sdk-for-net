package selftest

import (
	"context"
	"errors"
	"testing"
)

func TestRunnerPassesWhenChecksPass(t *testing.T) {
	runner := NewRunner(StaticCheck{CheckName: "ok"})
	result := runner.Run(context.Background())
	if !result.OK {
		t.Fatalf("expected OK result, got %#v", result.Errors)
	}
	if result.Sequence != 1 {
		t.Fatalf("expected sequence 1, got %d", result.Sequence)
	}
}

func TestRunnerCollectsErrors(t *testing.T) {
	runner := NewRunner(StaticCheck{CheckName: "bad", Err: errors.New("failed")})
	result := runner.Run(context.Background())
	if result.OK {
		t.Fatal("expected failing result")
	}
	if len(result.Errors) != 1 {
		t.Fatalf("expected one error, got %#v", result.Errors)
	}
}
