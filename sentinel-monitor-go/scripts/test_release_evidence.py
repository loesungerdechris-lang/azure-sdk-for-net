import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from release_evidence import prepare, seal, verify


def fixture(path, *, sbom=True, corrupt=False):
    files = {}

    def blob(value, media_type, **extra):
        data = json.dumps(value, separators=(",", ":")).encode()
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        files["blobs/sha256/" + digest.split(":")[1]] = data
        return {"mediaType": media_type, "digest": digest, "size": len(data), **extra}

    config = blob(
        {"architecture": "amd64", "os": "linux"},
        "application/vnd.oci.image.config.v1+json",
    )
    image = blob(
        {"schemaVersion": 2, "config": config, "layers": []},
        "application/vnd.oci.image.manifest.v1+json",
        platform={"os": "linux", "architecture": "amd64"},
    )
    types = ["https://slsa.dev/provenance/v1"] + (
        ["https://spdx.dev/Document"] if sbom else []
    )
    layers = [blob({"predicateType": t}, "application/vnd.in-toto+json") for t in types]
    attestation = blob(
        {"schemaVersion": 2, "config": config, "layers": layers},
        "application/vnd.oci.image.manifest.v1+json",
        platform={"os": "unknown", "architecture": "unknown"},
        annotations={
            "vnd.docker.reference.type": "attestation-manifest",
            "vnd.docker.reference.digest": image["digest"],
        },
    )
    root = blob(
        {"schemaVersion": 2, "manifests": [image, attestation]},
        "application/vnd.oci.image.index.v1+json",
    )
    files["index.json"] = json.dumps({"schemaVersion": 2, "manifests": [root]}).encode()
    files["oci-layout"] = b'{"imageLayoutVersion":"1.0.0"}'
    if corrupt:
        files["blobs/sha256/" + config["digest"].split(":")[1]] = b"changed"
    with tarfile.open(path, "w") as archive:
        for name, data in files.items():
            entry = tarfile.TarInfo(name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))
    report = {
        "ArtifactType": "container_image",
        "Metadata": {"ImageID": config["digest"]},
        "Results": [{"Target": "fixture", "Vulnerabilities": []}],
    }
    return root["digest"], report


class ReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.archive = Path(self.temp.name) / "image.tar"
        self.digest, self.report = fixture(self.archive)

    def record(self):
        return prepare(self.archive, self.digest, "a" * 40)

    def test_valid_scanned_archive_preserves_image_and_attestations(self):
        record = seal(self.record(), self.report)
        verify(self.archive, record, self.report)
        self.assertEqual(record["image_digest"], self.digest)
        self.assertIn("https://spdx.dev/Document", record["attestations"])

    def test_wrong_build_digest_is_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.archive, "sha256:" + "0" * 64, "a" * 40)

    def test_scan_layout_selects_the_verified_platform_without_changing_archive(self):
        before = self.archive.read_bytes()
        layout = Path(self.temp.name) / "scan"
        record = prepare(self.archive, self.digest, "a" * 40, layout)
        index = json.loads((layout / "index.json").read_text())
        self.assertEqual(len(index["manifests"]), 1)
        self.assertEqual(
            index["manifests"][0]["digest"], record["platform_manifest_digest"]
        )
        self.assertEqual(self.archive.read_bytes(), before)

    def test_missing_sbom_is_rejected(self):
        digest, _ = fixture(self.archive, sbom=False)
        with self.assertRaises(ValueError):
            prepare(self.archive, digest, "a" * 40)

    def test_changed_blob_is_rejected(self):
        digest, _ = fixture(self.archive, corrupt=True)
        with self.assertRaises(ValueError):
            prepare(self.archive, digest, "a" * 40)

    def test_changed_archive_is_rejected_before_publication(self):
        record = seal(self.record(), self.report)
        with self.archive.open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaises(ValueError):
            verify(self.archive, record, self.report)

    def test_high_vulnerability_is_rejected(self):
        self.report["Results"][0]["Vulnerabilities"] = [{"Severity": "HIGH"}]
        with self.assertRaises(ValueError):
            seal(self.record(), self.report)

    def test_scan_of_another_image_is_rejected(self):
        self.report["Metadata"]["ImageID"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            seal(self.record(), self.report)

    def test_missing_or_stale_scan_is_rejected(self):
        with self.assertRaises(ValueError):
            verify(self.archive, self.record(), self.report)
        record = seal(self.record(), self.report)
        record["scan_completed_at"] = (
            datetime.now(timezone.utc) - timedelta(days=2)
        ).isoformat()
        with self.assertRaises(ValueError):
            verify(self.archive, record, self.report)


if __name__ == "__main__":
    unittest.main()
