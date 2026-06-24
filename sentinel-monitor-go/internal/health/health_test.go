package health

import (
	"path/filepath"
	"testing"
	"time"
)

func TestCheckFileAcceptsFreshHealthyStatus(t *testing.T) {
	path := filepath.Join(t.TempDir(), "health.json")
	if err := Write(path, Healthy("test", 1, "ok")); err != nil {
		t.Fatalf("write health status: %v", err)
	}
	if err := CheckFile(path, time.Minute); err != nil {
		t.Fatalf("expected healthy status, got %v", err)
	}
}

func TestCheckFileRejectsFailedStatus(t *testing.T) {
	path := filepath.Join(t.TempDir(), "health.json")
	if err := Write(path, Failed("test", 1, "failed")); err != nil {
		t.Fatalf("write health status: %v", err)
	}
	if err := CheckFile(path, time.Minute); err == nil {
		t.Fatal("expected failed status to be rejected")
	}
}

func TestCheckFileRejectsMissingFile(t *testing.T) {
	path := filepath.Join(t.TempDir(), "missing.json")
	if err := CheckFile(path, time.Minute); err == nil {
		t.Fatal("expected missing file to be rejected")
	}
}
