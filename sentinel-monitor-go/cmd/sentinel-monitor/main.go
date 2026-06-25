package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/alerting"
	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/health"
	"github.com/loesungerdechris-lang/sentinel-monitor-go/internal/selftest"
)

const (
	defaultHealthPath    = "/tmp/sentinel/health.json"
	defaultCheckInterval = 60 * time.Second
	defaultHealthMaxAge  = 2 * time.Minute
	selfTestTimeout      = 10 * time.Second
	serviceName          = "sentinel-monitor-go"
)

func main() {
	healthPath := envOrDefault("HEALTH_PATH", defaultHealthPath)

	if len(os.Args) > 1 && os.Args[1] == "healthcheck" {
		if err := health.CheckFile(healthPath, defaultHealthMaxAge); err != nil {
			fmt.Printf("healthcheck_failed=%v\n", err)
			os.Exit(1)
		}
		fmt.Printf("healthcheck_ok=true health=%s\n", healthPath)
		return
	}

	interval := parseInterval(envOrDefault("SELF_TEST_INTERVAL", defaultCheckInterval.String()))
	runner := selftest.NewRunner(
		selftest.StaticCheck{CheckName: "evidence-chain-consistency"},
		selftest.StaticCheck{CheckName: "policy-registry-consistency"},
		selftest.StaticCheck{CheckName: "attestation-verifier-reachable"},
	)

	if ok := runSelfTestCycle(runner, healthPath); !ok {
		os.Exit(1)
	}

	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	ticker := time.NewTicker(interval)
	defer ticker.Stop()
	log.Printf("sentinel_monitor_daemon_started interval=%s health=%s", interval, healthPath)

	for {
		select {
		case <-ticker.C:
			_ = runSelfTestCycle(runner, healthPath)
		case <-ctx.Done():
			log.Println("sentinel_monitor_shutdown=true")
			return
		}
	}
}

func runSelfTestCycle(runner *selftest.Runner, healthPath string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), selfTestTimeout)
	defer cancel()

	result := runner.Run(ctx)
	if !result.OK {
		notifier := alerting.LogNotifier{}
		message := strings.Join(result.Errors, "; ")
		_ = notifier.Notify(ctx, alerting.Critical("SENTINEL self-test failed", "%s", message))
		if err := health.Write(healthPath, health.Failed(serviceName, result.Sequence, message)); err != nil {
			log.Printf("health_write_error=%v", err)
		}
		log.Printf("self_test_ok=false sequence=%d errors=%v", result.Sequence, result.Errors)
		return false
	}

	if err := health.Write(healthPath, health.Healthy(serviceName, result.Sequence, "all checks passed")); err != nil {
		log.Printf("health_write_error=%v", err)
		return false
	}
	log.Printf("self_test_ok=true sequence=%d health=%s", result.Sequence, healthPath)
	return true
}

func envOrDefault(name string, fallback string) string {
	value := os.Getenv(name)
	if value == "" {
		return fallback
	}
	return value
}

func parseInterval(value string) time.Duration {
	interval, err := time.ParseDuration(value)
	if err != nil || interval <= 0 {
		return defaultCheckInterval
	}
	return interval
}
