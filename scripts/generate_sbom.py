#!/usr/bin/env python3
"""Generate a deterministic CycloneDX SBOM from the installed runtime dependency graph."""

from __future__ import annotations

import argparse
import importlib.metadata as metadata
import json
import sys
import tomllib
import uuid
from collections import deque
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, cast
from urllib.parse import quote

from packaging.markers import default_environment
from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

PROJECT_ROOT: Final = Path(__file__).resolve().parent.parent
DEFAULT_REQUIREMENTS: Final = PROJECT_ROOT / "requirements.txt"
DEFAULT_OUTPUT: Final = PROJECT_ROOT / "dist" / "cognexus-runtime.cdx.json"
SERIAL_NAMESPACE: Final = uuid.UUID("6ac598e5-5204-50aa-bfcb-e09da563f70c")


@dataclass(frozen=True, slots=True)
class InstalledComponent:
    """Normalized installed distribution and its active dependency edges."""

    name: str
    version: str
    distribution: metadata.Distribution
    direct: bool
    requested: str | None
    active_extras: frozenset[str]

    @property
    def canonical_name(self) -> str:
        return canonicalize_name(self.name)

    @property
    def purl(self) -> str:
        package = quote(self.canonical_name, safe=".-_")
        version = quote(self.version, safe=".-_+")
        return f"pkg:pypi/{package}@{version}"


def _project_identity(pyproject: Path) -> tuple[str, str]:
    document = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = document.get("project")
    if not isinstance(project, dict):
        raise RuntimeError("pyproject.toml is missing [project]")
    name = project.get("name")
    version = project.get("version")
    if not isinstance(name, str) or not name.strip():
        raise RuntimeError("project.name must be a non-empty string")
    if not isinstance(version, str) or not version.strip():
        raise RuntimeError("project.version must be a non-empty string")
    return name.strip(), version.strip()


def _parse_requirement_file(path: Path, seen: set[Path] | None = None) -> list[Requirement]:
    resolved = path.resolve()
    visited = seen if seen is not None else set()
    if resolved in visited:
        raise RuntimeError(f"recursive requirement include detected: {resolved}")
    visited.add(resolved)
    requirements: list[Requirement] = []
    for line_number, raw in enumerate(resolved.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.split("#", maxsplit=1)[0].strip()
        if not line:
            continue
        if line.startswith(("-r ", "--requirement ")):
            include = line.split(maxsplit=1)[1].strip()
            requirements.extend(_parse_requirement_file(resolved.parent / include, visited))
            continue
        if line.startswith("-"):
            raise RuntimeError(
                f"unsupported requirement option in {resolved}:{line_number}: {line}"
            )
        try:
            requirement = Requirement(line)
        except InvalidRequirement as exc:
            raise RuntimeError(f"invalid requirement in {resolved}:{line_number}: {line}") from exc
        if requirement.url:
            raise RuntimeError(
                f"direct URL requirements are not permitted in release SBOM input: {line}"
            )
        requirements.append(requirement)
    visited.remove(resolved)
    return requirements


def _metadata_field(distribution: metadata.Distribution, key: str) -> str | None:
    package_metadata = distribution.metadata
    if key not in package_metadata:
        return None
    value = package_metadata[key]
    return value if isinstance(value, str) and value else None


def _installed_distributions() -> dict[str, metadata.Distribution]:
    result: dict[str, metadata.Distribution] = {}
    for distribution in metadata.distributions():
        name = _metadata_field(distribution, "Name")
        if not name:
            continue
        key = canonicalize_name(name)
        current = result.get(key)
        if current is not None and current.version != distribution.version:
            raise RuntimeError(
                f"multiple installed versions detected for {name}: "
                f"{current.version}, {distribution.version}"
            )
        result[key] = distribution
    return result


def _marker_applies(requirement: Requirement, extras: Iterable[str]) -> bool:
    if requirement.marker is None:
        return True
    environment = cast(dict[str, str], dict(default_environment()))
    contexts = {"", *extras}
    return any(requirement.marker.evaluate({**environment, "extra": extra}) for extra in contexts)


def _check_version(requirement: Requirement, installed_version: str) -> None:
    if not requirement.specifier:
        return
    try:
        version = Version(installed_version)
    except InvalidVersion as exc:
        raise RuntimeError(
            f"installed package {requirement.name} has an invalid version: {installed_version}"
        ) from exc
    if version not in requirement.specifier:
        raise RuntimeError(
            f"installed {requirement.name}=={installed_version} does not satisfy "
            f"{requirement.specifier}"
        )


def _resolve_graph(
    roots: list[Requirement],
) -> tuple[dict[str, InstalledComponent], dict[str, set[str]], list[str]]:
    installed = _installed_distributions()
    components: dict[str, InstalledComponent] = {}
    edges: dict[str, set[str]] = {}
    requested_by_name = {canonicalize_name(item.name): str(item) for item in roots}
    direct_names = set(requested_by_name)
    root_refs: list[str] = []
    queue: deque[tuple[Requirement, frozenset[str]]] = deque(
        (item, frozenset(item.extras)) for item in roots if _marker_applies(item, item.extras)
    )
    queued_extras: dict[str, set[str]] = {}

    while queue:
        requirement, inherited_extras = queue.popleft()
        key = canonicalize_name(requirement.name)
        distribution = installed.get(key)
        if distribution is None:
            raise RuntimeError(f"required distribution is not installed: {requirement.name}")
        _check_version(requirement, distribution.version)

        active_extras = frozenset({*inherited_extras, *requirement.extras})
        previous_extras = queued_extras.setdefault(key, set())
        extras_changed = not set(active_extras).issubset(previous_extras)
        previous_extras.update(active_extras)

        component = InstalledComponent(
            name=_metadata_field(distribution, "Name") or requirement.name,
            version=distribution.version,
            distribution=distribution,
            direct=key in direct_names,
            requested=requested_by_name.get(key),
            active_extras=frozenset(previous_extras),
        )
        was_new = key not in components
        components[key] = component
        edges.setdefault(key, set())
        if key in direct_names and component.purl not in root_refs:
            root_refs.append(component.purl)
        if not was_new and not extras_changed:
            continue

        for raw_dependency in distribution.requires or []:
            try:
                dependency = Requirement(raw_dependency)
            except InvalidRequirement as exc:
                raise RuntimeError(
                    f"invalid installed metadata requirement for {component.name}: {raw_dependency}"
                ) from exc
            if not _marker_applies(dependency, component.active_extras):
                continue
            dependency_key = canonicalize_name(dependency.name)
            dependency_distribution = installed.get(dependency_key)
            if dependency_distribution is None:
                raise RuntimeError(
                    f"installed metadata for {component.name} references missing active "
                    f"dependency {dependency.name}"
                )
            _check_version(dependency, dependency_distribution.version)
            dependency_purl = InstalledComponent(
                name=_metadata_field(dependency_distribution, "Name") or dependency.name,
                version=dependency_distribution.version,
                distribution=dependency_distribution,
                direct=dependency_key in direct_names,
                requested=requested_by_name.get(dependency_key),
                active_extras=frozenset(dependency.extras),
            ).purl
            edges[key].add(dependency_purl)
            queue.append((dependency, frozenset(dependency.extras)))

    return components, edges, sorted(root_refs)


def _component_document(component: InstalledComponent) -> dict[str, Any]:
    properties = [
        {"name": "cognexus:dependency:direct", "value": str(component.direct).lower()},
        {
            "name": "cognexus:dependency:active-extras",
            "value": ",".join(sorted(component.active_extras)),
        },
    ]
    if component.requested:
        properties.append({"name": "cognexus:dependency:requested", "value": component.requested})
    result: dict[str, Any] = {
        "type": "library",
        "bom-ref": component.purl,
        "name": component.name,
        "version": component.version,
        "purl": component.purl,
        "scope": "required",
        "properties": properties,
    }
    homepage = _metadata_field(component.distribution, "Home-page")
    if isinstance(homepage, str) and homepage.startswith(("https://", "http://")):
        result["externalReferences"] = [{"type": "website", "url": homepage}]
    return result


def generate(requirements: Path, pyproject: Path) -> dict[str, Any]:
    project_name, project_version = _project_identity(pyproject)
    root_requirements = _parse_requirement_file(requirements)
    components, edges, root_refs = _resolve_graph(root_requirements)
    ordered_components = sorted(
        components.values(), key=lambda item: (item.canonical_name, item.version)
    )
    application_ref = (
        f"pkg:pypi/{quote(canonicalize_name(project_name), safe='.-_')}@"
        f"{quote(project_version, safe='.-_+')}"
    )
    dependencies = [{"ref": application_ref, "dependsOn": root_refs}]
    dependencies.extend(
        {
            "ref": component.purl,
            "dependsOn": sorted(edges.get(component.canonical_name, set())),
        }
        for component in ordered_components
    )
    identity = json.dumps(
        {
            "application": application_ref,
            "components": [item.purl for item in ordered_components],
            "dependencies": dependencies,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid.uuid5(SERIAL_NAMESPACE, identity)}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "bom-ref": application_ref,
                "name": project_name,
                "version": project_version,
                "purl": application_ref,
            },
            "properties": [
                {
                    "name": "cognexus:sbom:source",
                    "value": "installed-runtime-dependency-closure",
                },
                {
                    "name": "cognexus:sbom:requirements",
                    "value": requirements.resolve().relative_to(PROJECT_ROOT).as_posix()
                    if requirements.resolve().is_relative_to(PROJECT_ROOT)
                    else str(requirements.resolve()),
                },
            ],
        },
        "components": [_component_document(item) for item in ordered_components],
        "dependencies": dependencies,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requirements", type=Path, default=DEFAULT_REQUIREMENTS)
    parser.add_argument("--pyproject", type=Path, default=PROJECT_ROOT / "pyproject.toml")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    try:
        document = generate(args.requirements, args.pyproject)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    except (OSError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"SBOM generation failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "status": "generated",
                "output": str(args.output),
                "components": len(document["components"]),
                "dependencies": len(document["dependencies"]),
                "serial_number": document["serialNumber"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
