#!/usr/bin/env python3
"""Cross-platform Cognexus bootstrap with network diagnostics and offline support."""

from __future__ import annotations

import argparse
import base64
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
import venv
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_VENV: Final = PROJECT_ROOT / ".venv"
RUNTIME_REQUIREMENTS: Final = PROJECT_ROOT / "requirements.txt"
DEVELOPMENT_REQUIREMENTS: Final = PROJECT_ROOT / "requirements-dev.txt"
RUNTIME_CONSTRAINTS: Final = PROJECT_ROOT / "constraints" / "runtime.txt"
SUPPORTED_PYTHON_MIN: Final = (3, 11)
SUPPORTED_PYTHON_MAX_EXCLUSIVE: Final = (3, 15)
DEFAULT_INDEX_URL: Final = "https://pypi.org/simple"
DEFAULT_TIMEOUT_SECONDS: Final = 15
DEFAULT_RETRIES: Final = 5
BOOTSTRAP_TOOLS: Final = (
    "pip>=26,<27",
    "setuptools>=80,<81",
    "wheel>=0.45,<1",
)


@dataclass(frozen=True, slots=True)
class NetworkProbe:
    """A non-secret connectivity result for one package index endpoint."""

    url: str
    host: str
    dns_ok: bool
    https_ok: bool
    detail: str

    @property
    def ok(self) -> bool:
        return self.dns_ok and self.https_ok


def _check_supported_python(version: tuple[int, int] | None = None) -> None:
    selected = version or sys.version_info[:2]
    if not (SUPPORTED_PYTHON_MIN <= selected < SUPPORTED_PYTHON_MAX_EXCLUSIVE):
        raise RuntimeError(
            "Cognexus requires Python 3.11-3.14; "
            f"found {selected[0]}.{selected[1]}. Use Python 3.12 when available."
        )


def _venv_python(venv_path: Path) -> Path:
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def _safe_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    hostname = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    path = parsed.path or "/"
    return urllib.parse.urlunsplit((parsed.scheme, f"{hostname}{port}", path, "", ""))


def _probe_index(
    index_url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    proxy: str | None = None,
    certificate: Path | None = None,
) -> NetworkProbe:
    normalized = index_url.rstrip("/") + "/openai-agents/"
    parsed = urllib.parse.urlsplit(normalized)
    host = parsed.hostname or ""
    host_port = host
    if parsed.port:
        host_port = f"{host}:{parsed.port}"
    request_url = urllib.parse.urlunsplit((parsed.scheme, host_port, parsed.path, parsed.query, ""))
    if parsed.scheme.lower() != "https":
        return NetworkProbe(
            request_url,
            host,
            False,
            False,
            "package index must use HTTPS",
        )
    if not host:
        return NetworkProbe(request_url, host, False, False, "index URL has no hostname")

    dns_host = host
    dns_port = parsed.port or 443
    if proxy:
        proxy_parts = urllib.parse.urlsplit(proxy)
        if not proxy_parts.hostname:
            return NetworkProbe(request_url, host, False, False, "proxy URL has no hostname")
        dns_host = proxy_parts.hostname
        dns_port = proxy_parts.port or 8080
    try:
        socket.getaddrinfo(dns_host, dns_port, type=socket.SOCK_STREAM)
    except OSError as exc:
        target = "proxy" if proxy else "package index"
        return NetworkProbe(
            request_url,
            host,
            False,
            False,
            f"DNS resolution failed for {target} host {dns_host}: {exc}",
        )

    handlers: list[urllib.request.BaseHandler] = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    opener = urllib.request.build_opener(*handlers)
    headers = {
        "Accept": "text/html,application/vnd.pypi.simple.v1+json",
        "User-Agent": "Cognexus-bootstrap/3.3.1",
    }
    if parsed.username is not None:
        username = urllib.parse.unquote(parsed.username)
        password = urllib.parse.unquote(parsed.password or "")
        encoded = base64.b64encode(f"{username}:{password}".encode()).decode("ascii")
        headers["Authorization"] = f"Basic {encoded}"
    request = urllib.request.Request(  # noqa: S310 -- HTTPS is enforced above.
        request_url, headers=headers, method="GET"
    )
    if certificate:
        import ssl

        context = ssl.create_default_context(cafile=str(certificate))
        opener = urllib.request.build_opener(
            *handlers, urllib.request.HTTPSHandler(context=context)
        )
    try:
        with opener.open(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            if 200 <= status < 400:
                return NetworkProbe(request_url, host, True, True, f"HTTPS status {status}")
            return NetworkProbe(request_url, host, True, False, f"unexpected HTTPS status {status}")
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            return NetworkProbe(
                normalized,
                host,
                True,
                True,
                f"index reachable but authentication is required (HTTP {exc.code})",
            )
        return NetworkProbe(request_url, host, True, False, f"HTTP error {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return NetworkProbe(request_url, host, True, False, f"HTTPS connection failed: {exc}")


def _print_probe(probe: NetworkProbe) -> None:
    status = "OK" if probe.ok else "FAILED"
    print(f"[{status}] package index: {_safe_url(probe.url)}")
    print(f"       host={probe.host or '<missing>'} dns={probe.dns_ok} https={probe.https_ok}")
    print(f"       detail={probe.detail}")


def _network_failure_help() -> str:
    return """
The dependency version is not the problem. The package index could not be reached.

Windows PowerShell checks:
  Resolve-DnsName pypi.org
  Test-NetConnection pypi.org -Port 443
  python -m pip config debug
  Get-ChildItem Env:PIP_*,Env:HTTP_PROXY,Env:HTTPS_PROXY

Common remediations:
  1. Confirm the browser can open https://pypi.org and try another network or hotspot.
  2. Disable a broken VPN/proxy, or pass your approved proxy with --proxy.
  3. On managed networks, pass the approved private index with --index-url.
  4. Flush stale DNS with: ipconfig /flushdns
  5. For an offline machine, build a wheelhouse on a matching connected machine and use
     --wheelhouse PATH. Do not use --trusted-host or disable TLS verification.
""".strip()


def _run(command: Sequence[str], *, cwd: Path = PROJECT_ROOT) -> None:
    printable = " ".join(_redact_argument(part) for part in command)
    print(f"+ {printable}", flush=True)
    completed = subprocess.run(command, cwd=cwd, check=False)  # noqa: S603
    if completed.returncode != 0:
        raise subprocess.CalledProcessError(completed.returncode, command)


def _redact_argument(value: str) -> str:
    if "://" not in value:
        return value
    parsed = urllib.parse.urlsplit(value)
    if parsed.username is None and parsed.password is None:
        return value
    host = parsed.hostname or ""
    port = f":{parsed.port}" if parsed.port else ""
    return urllib.parse.urlunsplit((parsed.scheme, f"***:***@{host}{port}", parsed.path, "", ""))


def _pip_index_arguments(args: argparse.Namespace) -> list[str]:
    result = ["--index-url", args.index_url]
    for value in args.extra_index_url:
        result.extend(("--extra-index-url", value))
    if args.proxy:
        result.extend(("--proxy", args.proxy))
    if args.cert:
        result.extend(("--cert", str(args.cert)))
    result.extend(("--timeout", str(args.timeout), "--retries", str(args.retries)))
    return result


def _pip_install_command(
    python: Path,
    *,
    requirements: Path,
    constraints: Path,
    args: argparse.Namespace,
) -> list[str]:
    command = [str(python), "-m", "pip", "install", "--disable-pip-version-check"]
    if args.wheelhouse:
        command.extend(("--no-index", "--find-links", str(args.wheelhouse.resolve())))
    else:
        command.extend(_pip_index_arguments(args))
    command.extend(("-r", str(requirements), "-c", str(constraints)))
    return command


def _upgrade_bootstrap_tools(python: Path, args: argparse.Namespace) -> None:
    if args.no_upgrade_tools:
        return
    command = [str(python), "-m", "pip", "install", "--disable-pip-version-check"]
    if args.wheelhouse:
        command.extend(("--no-index", "--find-links", str(args.wheelhouse.resolve())))
    else:
        command.extend(_pip_index_arguments(args))
    command.extend(BOOTSTRAP_TOOLS)
    _run(command)


def _create_or_reuse_venv(path: Path, recreate: bool) -> Path:
    if recreate and path.exists():
        shutil.rmtree(path)
    python = _venv_python(path)
    if not python.is_file():
        print(f"Creating virtual environment: {path}")
        venv.EnvBuilder(with_pip=True, clear=False).create(path)
    if not python.is_file():
        raise RuntimeError(f"virtual-environment interpreter was not created: {python}")
    return python


def _prepare_local_files() -> None:
    environment = PROJECT_ROOT / ".env"
    example = PROJECT_ROOT / ".env.example"
    if not environment.exists() and example.is_file():
        shutil.copyfile(example, environment)
        print("Created .env from .env.example; add OPENAI_API_KEY only for live runs.")
    for directory in (PROJECT_ROOT / "data", PROJECT_ROOT / "logs"):
        directory.mkdir(parents=True, exist_ok=True)


def _download_wheelhouse(destination: Path, args: argparse.Namespace) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    requirements = RUNTIME_REQUIREMENTS if args.runtime_only else DEVELOPMENT_REQUIREMENTS
    command = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "--disable-pip-version-check",
        "--dest",
        str(destination.resolve()),
        "-r",
        str(requirements),
        "-c",
        str(RUNTIME_CONSTRAINTS),
        *_pip_index_arguments(args),
        *BOOTSTRAP_TOOLS,
    ]
    _run(command)
    print(f"Wheelhouse created at: {destination.resolve()}")
    print("Copy that directory to the offline machine and run:")
    print(f"  python scripts/bootstrap.py --wheelhouse {destination.name}")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venv", type=Path, default=DEFAULT_VENV)
    parser.add_argument("--runtime-only", action="store_true")
    parser.add_argument("--recreate-venv", action="store_true")
    parser.add_argument("--diagnose-only", action="store_true")
    parser.add_argument("--skip-network-check", action="store_true")
    parser.add_argument("--wheelhouse", type=Path)
    parser.add_argument("--download-wheelhouse", type=Path)
    parser.add_argument("--index-url", default=os.getenv("PIP_INDEX_URL", DEFAULT_INDEX_URL))
    parser.add_argument(
        "--extra-index-url",
        action="append",
        default=[],
        help="Additional approved package index; may be repeated.",
    )
    parser.add_argument("--proxy", default=os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY"))
    parser.add_argument("--cert", type=Path)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    parser.add_argument("--no-upgrade-tools", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        _check_supported_python()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.timeout < 1 or args.retries < 0:
        print(
            "ERROR: --timeout must be positive and --retries cannot be negative.", file=sys.stderr
        )
        return 2
    if args.cert and not args.cert.is_file():
        print(f"ERROR: certificate file not found: {args.cert}", file=sys.stderr)
        return 2
    if args.wheelhouse and args.download_wheelhouse:
        print("ERROR: use either --wheelhouse or --download-wheelhouse, not both.", file=sys.stderr)
        return 2
    if args.wheelhouse and not args.wheelhouse.is_dir():
        print(f"ERROR: wheelhouse directory not found: {args.wheelhouse}", file=sys.stderr)
        return 2

    if not args.wheelhouse and not args.skip_network_check:
        probe = _probe_index(
            args.index_url,
            timeout=args.timeout,
            proxy=args.proxy,
            certificate=args.cert,
        )
        _print_probe(probe)
        sys.stdout.flush()
        if not probe.ok:
            print("\n" + _network_failure_help(), file=sys.stderr)
            return 3
    elif args.wheelhouse:
        print(f"Using offline wheelhouse: {args.wheelhouse.resolve()}")

    if args.diagnose_only:
        return 0

    try:
        if args.download_wheelhouse:
            _download_wheelhouse(args.download_wheelhouse, args)
            return 0

        python = _create_or_reuse_venv(args.venv.resolve(), args.recreate_venv)
        _upgrade_bootstrap_tools(python, args)
        requirements = RUNTIME_REQUIREMENTS if args.runtime_only else DEVELOPMENT_REQUIREMENTS
        _run(
            _pip_install_command(
                python,
                requirements=requirements,
                constraints=RUNTIME_CONSTRAINTS,
                args=args,
            )
        )
        _run((str(python), "-m", "pip", "check"))
        _run((str(python), str(PROJECT_ROOT / "scripts" / "verify_runtime_lock.py")))
        _prepare_local_files()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: Cognexus bootstrap failed: {exc}", file=sys.stderr)
        if not args.wheelhouse:
            print("\n" + _network_failure_help(), file=sys.stderr)
        return 1

    print("Cognexus dependencies installed and verified successfully.")
    if os.name == "nt":
        print(r"Activate with: .\.venv\Scripts\Activate.ps1")
    else:
        print("Activate with: source .venv/bin/activate")
    print("Validate with: python scripts/quality_gate.py --quick")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
