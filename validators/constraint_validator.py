"""Machine-enforced NEXUS architecture constraints."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

from validators.arch02_validator import Arch02Validator
from validators.arch04_validator import Arch04Validator


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Constraint validation result."""

    passed: bool
    violations: list[dict[str, str]]
    warnings: list[dict[str, str]]

    @property
    def should_reject(self) -> bool:
        """Return whether the output must be regenerated."""
        return bool(self.violations)

    @property
    def rejection_prompt(self) -> str:
        """Build a correction prompt from violations."""
        return "\n".join(
            ["[SYSTEM] Correct these constraint violations:"]
            + [f"- {item['code']}: {item['rejection_prompt']}" for item in self.violations]
        )


class ConstraintValidator:
    """Validate generated text against ARCH-02 through ARCH-10 rules."""

    def validate(self, text: str) -> ValidationResult:
        """Run all deterministic validators."""
        violations: list[dict[str, str]] = []
        for rule in self._rules():
            finding = rule(text)
            if finding:
                violations.append(finding)
        return ValidationResult(not violations, violations, [])

    def _rules(self) -> list[Callable[[str], dict[str, str] | None]]:
        return [
            Arch02Validator().validate,
            Arch04Validator().validate,
            self._arch03,
            self._arch05,
            self._arch06,
            self._arch07,
            self._arch08,
            self._arch09,
            self._arch10,
        ]

    def _arch03(self, text: str) -> dict[str, str] | None:
        if re.search(
            r"\b(?:getServerSideProps|getStaticProps|getInitialProps|ReactDOM\.render)\b", text
        ):
            return self._finding(
                "ARCH-03",
                "Deprecated Next.js/React API detected.",
                "Use Next.js 15 and React 19 patterns.",
            )
        return None

    def _arch05(self, text: str) -> dict[str, str] | None:
        if re.search(r"async\s+(?:function\s+)?\w*Service\w*", text) and "Effect" not in text:
            return self._finding(
                "ARCH-05",
                "Backend service bypasses Effect-TS Layer discipline.",
                "Model the service with Effect and Layer.",
            )
        return None

    def _arch06(self, text: str) -> dict[str, str] | None:
        roles = len(re.findall(r"new\s+(?:Queue|Worker|QueueEvents)\b", text))
        connections = len(re.findall(r"new\s+(?:IORedis|Redis)\b", text))
        if roles >= 2 and connections < roles:
            return self._finding(
                "ARCH-06",
                "BullMQ roles appear to share Redis connections.",
                "Use one Redis connection per Queue, Worker, and QueueEvents role.",
            )
        return None

    def _arch07(self, text: str) -> dict[str, str] | None:
        for value in re.findall(r"maxTsServerMemory[\"'\s:=]+(\d+)", text, re.I):
            if int(value) > 3072:
                return self._finding(
                    "ARCH-07",
                    f"maxTsServerMemory={value} exceeds 3072.",
                    "Set maxTsServerMemory to 3072 or less.",
                )
        return None

    def _arch08(self, text: str) -> dict[str, str] | None:
        lower = text.lower()
        if "edge" in lower and any(
            item in lower for item in ("jsonwebtoken", "jwt-simple", "express-jwt")
        ):
            return self._finding(
                "ARCH-08",
                "Node-only JWT library used in Edge Runtime.",
                "Use an Edge-compatible library such as jose.",
            )
        return None

    def _arch09(self, text: str) -> dict[str, str] | None:
        if "swarmx" in text.lower() and re.search(
            r"this\.(?:state|memory|history)\s*=", text, re.I
        ):
            return self._finding(
                "ARCH-09",
                "SwarmX agent stores in-memory state.",
                "Externalize state and keep agent instances stateless.",
            )
        return None

    def _arch10(self, text: str) -> dict[str, str] | None:
        lower = text.lower()
        write = "taxbridge" in lower and any(
            word in lower for word in ("create", "update", "delete", "write", "invoice", "post")
        )
        if write and not any(word in lower for word in ("idempotency", "x-idempotency-key")):
            return self._finding(
                "ARCH-10",
                "TaxBridge write lacks idempotency handling.",
                "Require and persist X-Idempotency-Key.",
            )
        return None

    @staticmethod
    def _finding(code: str, description: str, prompt: str) -> dict[str, str]:
        return {
            "code": code,
            "severity": "P1",
            "description": description,
            "rejection_prompt": prompt,
        }
