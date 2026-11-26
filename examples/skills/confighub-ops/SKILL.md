---
name: confighub-ops
description: Shared operational memory and safe change workflow for coding agents (Claude Code, Codex, Antigravity) working against a ConfigHub hub.
---

# ConfigHub Ops Skill

Use this skill whenever you inspect, change, harden, or debug application configuration managed in a ConfigHub hub (local `confighub mini`, hosted `hub.confighub.com`, or self-hosted behind SSO).

## Rules

1. **Keep your assigned identity.** Always run with your own scoped `CUB_CONFIG` and `CUB_CONTEXT` (for example `claude-dev`, `codex-ops`, or `agy-oncall`). Never reuse another person's or another agent's sign-in.
2. **Inspect ConfigHub before changing anything.** Do not guess from Git alone or rely on another agent's chat history. Read live values and reasons first:
   ```sh
   cub unit data --space APP-staging app
   cub revision list --space APP-base app
   ```
3. **Never bypass the hub.** Do not run `kubectl apply`, `kubectl edit`, `kubectl patch`, `fly secrets set`, or `vercel env add` directly against production. Propose changes through ConfigHub so every value keeps its reason and waits for human approval.
4. **Always explain why.** Every write must carry `--change-desc` naming what changed and why, so the next agent or on-call engineer waking up cold can trace the decision in seconds:
   ```sh
   cub mini set APP KEY=VALUE --variant staging --change-desc "Reason for change"
   ```
5. **Respect production approvals and guards.** You may update `staging` and propose changes to `live`, and you must never approve your own production change or bypass a guarded key. Leave the approve command for the human owner.
6. **Make surgical forward fixes.** During an incident, read prior agents' `--change-desc` history, fix the colliding setting cleanly with a new revision, and preserve earlier HA/rate-limit/pricing settings rather than blindly reverting.
