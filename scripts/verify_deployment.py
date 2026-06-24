#!/usr/bin/env python3
"""Verify Cognexus container/Kubernetes controls and optionally probe a live deployment."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Final
from urllib.parse import urlsplit

import yaml

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
KUBE_ROOT: Final = PROJECT_ROOT / "deploy" / "kubernetes"
REQUIRED_KUBE_FILES: Final = {
    "namespace.yaml",
    "service-account.yaml",
    "configmap.yaml",
    "deployment.yaml",
    "service.yaml",
    "hpa.yaml",
    "pdb.yaml",
    "network-policy.yaml",
}


def _load(path: Path) -> dict[str, Any]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError(f"{path} must contain one YAML object")
    return document


def _nested(document: dict[str, Any], *path: str) -> Any:
    current: Any = document
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise RuntimeError(f"missing deployment field: {'.'.join(path)}")
        current = current[key]
    return current


def validate_static() -> list[str]:
    evidence: list[str] = []
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    for pattern, description in (
        (r"(?m)^USER\s+10001:10001$", "non-root runtime user"),
        (r"(?m)^HEALTHCHECK\s", "container healthcheck"),
        (r"readOnlyRootFilesystem:\s*true", "read-only root filesystem"),
    ):
        source = (
            dockerfile
            if "read-only" not in description
            else (KUBE_ROOT / "deployment.yaml").read_text(encoding="utf-8")
        )
        if re.search(pattern, source) is None:
            raise RuntimeError(f"missing {description}")
        evidence.append(description)

    kustomization = _load(KUBE_ROOT / "kustomization.yaml")
    resources = set(kustomization.get("resources", []))
    missing = REQUIRED_KUBE_FILES - resources
    if missing:
        raise RuntimeError(f"kustomization missing resources: {', '.join(sorted(missing))}")
    evidence.append("complete Kubernetes resource set")

    deployment = _load(KUBE_ROOT / "deployment.yaml")
    spec = _nested(deployment, "spec")
    replicas = spec.get("replicas")
    if not isinstance(replicas, int) or replicas < 2:
        raise RuntimeError("deployment must run at least two replicas")
    pod_spec = _nested(deployment, "spec", "template", "spec")
    if pod_spec.get("automountServiceAccountToken") is not False:
        raise RuntimeError("service-account token automount must be disabled")
    pod_security = pod_spec.get("securityContext", {})
    if not isinstance(pod_security, dict) or pod_security.get("runAsNonRoot") is not True:
        raise RuntimeError("pod must require a non-root user")
    containers = pod_spec.get("containers")
    if (
        not isinstance(containers, list)
        or len(containers) != 1
        or not isinstance(containers[0], dict)
    ):
        raise RuntimeError("deployment must define exactly one API container")
    container = containers[0]
    image = str(container.get("image", ""))
    if not image or "OWNER/REPOSITORY" in image or image.endswith(":latest") or ":" not in image:
        raise RuntimeError("deployment image must be concrete and immutably version-tagged")
    for probe in ("startupProbe", "livenessProbe", "readinessProbe"):
        if probe not in container:
            raise RuntimeError(f"deployment is missing {probe}")
    resources_spec = container.get("resources")
    if (
        not isinstance(resources_spec, dict)
        or not resources_spec.get("requests")
        or not resources_spec.get("limits")
    ):
        raise RuntimeError("container resources must define requests and limits")
    security = container.get("securityContext", {})
    if not isinstance(security, dict):
        raise RuntimeError("container securityContext must be a mapping")
    if (
        security.get("allowPrivilegeEscalation") is not False
        or security.get("readOnlyRootFilesystem") is not True
    ):
        raise RuntimeError("container must disable privilege escalation and use a read-only root")
    capabilities = security.get("capabilities", {})
    if not isinstance(capabilities, dict) or capabilities.get("drop") != ["ALL"]:
        raise RuntimeError("container must drop all Linux capabilities")
    evidence.extend(
        [
            "versioned container image",
            "startup/liveness/readiness probes",
            "resource bounds",
            "restricted container security context",
        ]
    )

    configmap = _load(KUBE_ROOT / "configmap.yaml")
    data = configmap.get("data", {})
    if not isinstance(data, dict):
        raise RuntimeError("ConfigMap data must be a mapping")
    forbidden = {
        key
        for key in data
        if any(token in key.upper() for token in ("SECRET", "PASSWORD", "API_KEY", "TOKEN"))
    }
    if forbidden:
        raise RuntimeError(
            f"ConfigMap contains secret-shaped fields: {', '.join(sorted(forbidden))}"
        )
    if (
        data.get("NEXUS_ALLOW_SQLITE_FALLBACK") != "false"
        or data.get("NEXUS_ALLOW_STATELESS_FALLBACK") != "false"
    ):
        raise RuntimeError("production state fallback must be disabled")
    evidence.append("fail-closed production state configuration")
    return evidence


def _request(
    url: str, *, api_key: str | None = None, payload: dict[str, Any] | None = None
) -> tuple[int, Any]:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError("deployment probe URL must use http:// or https://")
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["X-API-Key"] = api_key
    request = urllib.request.Request(  # noqa: S310 -- scheme restricted above
        url, data=body, headers=headers, method="POST" if body else "GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{url} returned HTTP {exc.code}: {raw[:300]}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{url} probe failed: {exc}") from exc


def validate_live(base_url: str, api_key: str | None) -> list[str]:
    root = base_url.rstrip("/")
    evidence: list[str] = []
    for path, expected in (("/health", "ok"), ("/ready", "ready")):
        status, body = _request(root + path)
        if status != 200 or not isinstance(body, dict) or body.get("status") != expected:
            raise RuntimeError(f"{path} did not return status={expected}")
        evidence.append(f"live {path} probe")
    if api_key:
        status, body = _request(
            root + "/v1/skills/recommend",
            api_key=api_key,
            payload={"message": "Review production release safety", "execution_mode": "review"},
        )
        if status != 200 or not isinstance(body, dict) or body.get("execution_mode") != "review":
            raise RuntimeError("authenticated recommendation smoke test failed")
        evidence.append("authenticated skill recommendation smoke test")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url", help="Optional deployed service root, such as https://api.example.com"
    )
    parser.add_argument("--api-key", help="Optional API key for authenticated smoke verification")
    args = parser.parse_args()
    try:
        evidence = validate_static()
        if args.base_url:
            evidence.extend(validate_live(args.base_url, args.api_key))
    except (OSError, RuntimeError, yaml.YAMLError) as exc:
        print(f"deployment verification failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "verified", "evidence": evidence}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
