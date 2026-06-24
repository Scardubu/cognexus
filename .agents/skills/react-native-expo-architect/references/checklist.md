# React Native Expo Architect checklist

## Mandatory checks

- Confirm supported Expo/React Native versions, device classes, offline behavior, and native capabilities.
- Design for intermittent networks, app lifecycle transitions, permissions, and constrained devices.
- Keep native dependencies compatible with the selected build workflow and deployment channels.
- Validate accessibility, touch targets, keyboard behavior, safe areas, and reduced motion.
- Include release, rollback, telemetry, and store-review implications.
- Test on representative Android and iOS devices, not only simulators.

## Source topic map

The supplied skill contained the following major sections. Load `guidance.md` only for sections relevant to the task:

- `SDK 54 Critical Facts`
- `Protocol`
- `Step 1 — Project Setup`
- `Step 2 — Expo Router v4 Navigation`
- `Step 3 — Reanimated v4 (New Architecture Only)`
- `Step 4 — Shared Code (Web + Mobile)`
- `Step 5 — EAS Build Configuration`
- `Step 6 — OTA Updates (expo-updates)`
- `Quality Gates`
- `Activation Triggers`
- `Skill Chain`

## Completion evidence

- [ ] Scope and assumptions are explicit.
- [ ] High-risk actions have approval gates.
- [ ] Inputs and outputs are validated.
- [ ] Failure and rollback behavior are documented.
- [ ] Security and privacy implications are addressed.
- [ ] Tests or deterministic validation have run.
- [ ] Observability and maintenance implications are covered.
- [ ] No secrets or sensitive data appear in output.
