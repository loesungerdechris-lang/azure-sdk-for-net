package main

import (
	"context"
	"fmt"
	"time"

	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/alerting"
	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/health"
	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/selftest"
)

const healthPath = "health.json"

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	runner := selftest.NewRunner(
		selftest.StaticCheck{CheckName: "evidence-chain-consistency"},
		selftest.StaticCheck{CheckName: "policy-registry-consistency"},
		selftest.StaticCheck{CheckName: "attestation-verifier-reachable"},
	)

	result := runner.Run(ctx)
	if !result.OK {
		notifier := alerting.LogNotifier{}
		_ = notifier.Notify(ctx, alerting.Critical("SENTINEL self-test failed", "%v", result.Errors))
		fmt.Printf("self_test_ok=false errors=%v\n", result.Errors)
		return
	}

	status := health.Healthy("sentinel-monitor-go", result.Sequence, "all checks passed")
	if err := health.Write(healthPath, status); err != nil {
		fmt.Printf("health_write_error=%v\n", err)
		return
	}
	fmt.Printf("self_test_ok=true sequence=%d health=%s\n", result.Sequence, healthPath)
}
