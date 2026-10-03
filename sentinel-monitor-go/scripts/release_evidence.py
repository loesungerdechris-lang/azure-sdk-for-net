"""Bind an offline image scan and its attestations to the bytes promoted to GHCR."""

import argparse
import hashlib
import json
import os
import re
import tarfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")
BLOB_RE = re.compile(r"blobs/sha256/[0-9a-f]{64}")


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def archive_files(archive):
    files = {}
    with tarfile.open(archive) as stream:
        for entry in stream:
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Unsafe OCI archive path")
            if entry.isdir():
                continue
            name = str(path)
            if not entry.isfile() or name in files:
                raise ValueError("OCI archive must contain unique regular files")
            if name not in {"oci-layout", "index.json"} and not BLOB_RE.fullmatch(name):
                raise ValueError("Unexpected OCI archive member")
            files[name] = stream.extractfile(entry).read()
            if BLOB_RE.fullmatch(name) and sha256(files[name]) != path.name:
                raise ValueError("OCI blob checksum mismatch")
    return files


def prepare(archive, digest, commit, layout=None):
    if not DIGEST_RE.fullmatch(digest) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Invalid build digest or source commit")
    files = archive_files(archive)

    def read_blob(descriptor):
        key = descriptor.get("digest", "")
        if not DIGEST_RE.fullmatch(key):
            raise ValueError("Invalid OCI descriptor digest")
        data = files.get("blobs/sha256/" + key.split(":")[1])
        if data is None or len(data) != descriptor.get("size"):
            raise ValueError("Missing or truncated OCI blob")
        return data

    if json.loads(files["oci-layout"]).get("imageLayoutVersion") != "1.0.0":
        raise ValueError("Unsupported OCI layout")
    roots = json.loads(files["index.json"]).get("manifests", [])
    if len(roots) != 1 or roots[0].get("digest") != digest:
        raise ValueError("Archive does not contain the expected build digest")
    manifests = json.loads(read_blob(roots[0])).get("manifests", [])
    images = [
        d
        for d in manifests
        if d.get("platform") == {"os": "linux", "architecture": "amd64"}
    ]
    if len(images) != 1:
        raise ValueError("Expected exactly one linux/amd64 image")
    image = images[0]
    manifest = json.loads(read_blob(image))
    config = manifest["config"]
    for layer in manifest["layers"]:
        read_blob(layer)
    config_data = json.loads(read_blob(config))
    if config_data.get("architecture") != "amd64" or config_data.get("os") != "linux":
        raise ValueError("Image configuration does not match the scanned platform")
    predicates = set()
    for descriptor in manifests:
        if descriptor == image:
            continue
        annotations = descriptor.get("annotations", {})
        if (
            annotations.get("vnd.docker.reference.type") != "attestation-manifest"
            or annotations.get("vnd.docker.reference.digest") != image["digest"]
        ):
            raise ValueError(
                "Unscanned image or unrelated attestation in release index"
            )
        attestation = json.loads(read_blob(descriptor))
        read_blob(attestation["config"])
        for layer in attestation["layers"]:
            statement = json.loads(read_blob(layer))
            predicates.add(statement.get("predicateType", ""))
    if "https://spdx.dev/Document" not in predicates:
        raise ValueError("SBOM attestation is missing")
    if not predicates.intersection(
        {"https://slsa.dev/provenance/v0.2", "https://slsa.dev/provenance/v1"}
    ):
        raise ValueError("Build provenance attestation is missing")
    if layout is not None:
        for name, data in files.items():
            path = Path(layout) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return {
        "schema_version": "sentinel-monitor-release-evidence-v1",
        "source_commit": commit,
        "image_digest": digest,
        "platform_manifest_digest": image["digest"],
        "config_digest": config["digest"],
        "oci_archive_sha256": sha256(Path(archive).read_bytes()),
        "attestations": sorted(predicates),
        "scan_status": "PENDING",
    }


def seal(record, report):
    if (
        report.get("ArtifactType") != "container_image"
        or report.get("Metadata", {}).get("ImageID") != record["config_digest"]
    ):
        raise ValueError("Scan does not refer to the image being published")
    results = report.get("Results")
    if not isinstance(results, list) or not results:
        raise ValueError("Scan inventory is missing")
    for result in results:
        for finding in result.get("Vulnerabilities") or []:
            if finding.get("Severity") in {"HIGH", "CRITICAL"}:
                raise ValueError("Release blocked by HIGH/CRITICAL vulnerability")
    return {
        **record,
        "scan_status": "PASS",
        "scan_completed_at": datetime.now(timezone.utc).isoformat(),
        "scan_report_sha256": sha256(json_bytes(report)),
        "scanner": "Trivy v0.75.0",
    }


def verify(archive, record, report):
    if record.get("scan_status") != "PASS":
        raise ValueError("A successful pre-publication scan is required")
    actual = prepare(archive, record["image_digest"], record["source_commit"])
    for key, value in actual.items():
        if key != "scan_status" and record.get(key) != value:
            raise ValueError("Release archive no longer matches the scanned evidence")
    seal(actual, report)
    if record.get("scan_report_sha256") != sha256(json_bytes(report)):
        raise ValueError("Scan report checksum mismatch")
    completed = datetime.fromisoformat(record["scan_completed_at"])
    age = (datetime.now(timezone.utc) - completed).total_seconds()
    if not 0 <= age <= 24 * 60 * 60:
        raise ValueError("Scan must have completed within the last 24 hours")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "seal", "verify"])
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--digest")
    parser.add_argument("--commit")
    parser.add_argument("--layout", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--expected-evidence-sha")
    args = parser.parse_args()
    if args.operation == "prepare":
        record = prepare(args.archive, args.digest, args.commit, args.layout)
    else:
        if args.operation == "verify":
            if (
                not args.expected_evidence_sha
                or sha256(args.evidence.read_bytes()) != args.expected_evidence_sha
            ):
                raise ValueError(
                    "Evidence does not match the successful build-and-scan job"
                )
        record = json.loads(args.evidence.read_text())
        report = json.loads(args.report.read_text())
        if args.operation == "seal":
            record = seal(record, report)
        else:
            verify(args.archive, record, report)
    if args.operation != "verify":
        args.evidence.write_bytes(json_bytes(record))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
            output.write(
                f"platform_manifest_digest={record['platform_manifest_digest']}\n"
            )
            output.write(f"evidence_sha256={sha256(args.evidence.read_bytes())}\n")
    print(f"{args.operation}: verified {record['image_digest']}")


if __name__ == "__main__":
    main()
