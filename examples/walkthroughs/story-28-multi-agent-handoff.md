<!-- walkthrough
id: story-28-multi-agent-handoff
story: 28
starts_with: both
needs: [confighub mini package or a shared ConfigHub hub]
budget_seconds: 180
-->
# 28. Three agents, zero shared chat history, one operational memory

Three engineers work on the same service (`fx-api`) using three different AI coding agents — **Claude Code** (`claude-dev`), **Codex** (`codex-ops`), and **Antigravity** (`agy-oncall`) — with zero shared chat transcripts. Each agent has its own scoped ConfigHub service account and one thin shared skill ([`examples/skills/confighub-ops/SKILL.md`](../skills/confighub-ops/SKILL.md)):

- **Agent 1 (`claude-dev`)** ships a 1-second live FX ticker (`FX_POLL_INTERVAL_MS=1000`) to staging.
- **Agent 2 (`codex-ops`)** wakes up cold, reads `claude-dev`'s recorded reason in ConfigHub, hardens production with a 10 RPM vendor rate limit (`FX_RATE_LIMIT_RPM=10`) and `FX_CACHE_TTL_SEC=0`, and is refused when it tries to approve production itself; the human owner approves.
- **Agent 3 (`agy-oncall`)** wakes up cold at 2 AM during HTTP 429 rate-limit errors, traces both prior decisions from ConfigHub's revision history in seconds, and proposes a surgical forward fix (`FX_CACHE_TTL_SEC=15`) without reverting the 1-second ticker, dropping the rate limit, or touching `FX_SPREAD_BPS=25`.

A **hub** is a ConfigHub server and database that stores your app's settings, the reason for each value, and who approved each change — locally on your laptop, hosted on `confighub.com`, or self-hosted in your cluster.

## Quick start

You need: `cub` with a local hub ([install the local hub](../../docs/install-mini.md)) or a shared hub, and the portable skill [`examples/skills/confighub-ops/SKILL.md`](../skills/confighub-ops/SKILL.md).

| | By hand | Ask your agent |
|---|---|---|
| Adopt the app and issue scoped keys | `cub mini adopt . --name fx-api` then `cub mini require-approval fx-api --variant live --agent claude-dev` (repeat for `codex-ops`, `agy-oncall`) | "Adopt `fx-api` into ConfigHub and create scoped agent keys for dev, ops, and on-call." |
| Agent 1 ships to staging | `CUB_CONTEXT=claude-dev cub mini set fx-api FX_POLL_INTERVAL_MS=1000 --variant staging --change-desc "1s live FX ticker"` | "Set `FX_POLL_INTERVAL_MS=1000` in staging with a clear reason." |
| Agent 2 inspects cold and hardens | `CUB_CONTEXT=codex-ops cub revision list --space fx-api-staging app` then propose hardening to `live` | "Inspect what changed in staging, harden rate limits and cache for prod, and propose it for approval." |
| Agent 3 fixes 2 AM incident cold | `CUB_CONTEXT=agy-oncall cub revision list --space fx-api-live app` then propose `FX_CACHE_TTL_SEC=15` | "Check `fx-api-live` history for why 429s started and propose a surgical fix without reverting the ticker or touching `FX_SPREAD_BPS`." |
| Human approves production | `cub mini approve ORDER` (agents are refused by the hub) | You approve production yourself. |

Without ConfigHub: each agent only sees its own local chat transcript and static Git files, so an on-call agent at 2 AM has to guess why a setting exists or blindly revert a whole release.

**Where this grows (1:46 video):** Watch the [ConfigHub Trailer](https://youtu.be/H7xtSqMZrao) to see this exact `cub unit blame` + approval + field-guard workflow running across multi-region Kubernetes fleets with Argo CD, Flux, and Sveltos.

## Deeper dive

<details>
<summary>Show the full walkthrough</summary>

## Human

### What you need

A local hub (`cub mini install`) or shared hub, and an app folder with `.env` containing `FX_POLL_INTERVAL_MS=5000`, `FX_RATE_LIMIT_RPM=60`, `FX_CACHE_TTL_SEC=30`, and `FX_SPREAD_BPS=25`.

### Steps

1. Adopt `fx-api` and create three scoped agent keys:
   <!-- run: setup -->
   ```sh
   cub mini adopt . --name fx-api
   cub mini approve fx-api --yes
   cub mini require-approval fx-api --variant live --agent claude-dev --try staging
   cub mini require-approval fx-api --variant live --agent codex-ops
   cub mini require-approval fx-api --variant live --agent agy-oncall
   ```

2. As `claude-dev`, ship the 1-second ticker to staging with a reason:
   <!-- run: act1 -->
   ```sh
   CUB_CONFIG="$HOME/.confighub-agent-claude-dev" CUB_CONTEXT=claude-dev \
     cub mini set fx-api FX_POLL_INTERVAL_MS=1000 --variant staging \
     --change-desc "claude-dev: 1s live FX ticker for Harbor Bank FX desk"
   ```

3. As `codex-ops` (zero shared chat), read staging's history and propose the hardened production values:
   <!-- run: act2 -->
   ```sh
   CUB_CONFIG="$HOME/.confighub-agent-codex-ops" CUB_CONTEXT=codex-ops \
     cub revision list --space fx-api-staging app
   CUB_CONFIG="$HOME/.confighub-agent-codex-ops" CUB_CONTEXT=codex-ops \
     cub mini set fx-api FX_POLL_INTERVAL_MS=1000 FX_RATE_LIMIT_RPM=10 FX_CACHE_TTL_SEC=0 --variant live \
     --change-desc "codex-ops: carry 1s ticker, enforce 10 RPM per-pod vendor cap, disable stale quote cache"
   ```

4. Verify that `codex-ops` cannot self-approve any waiting order, then approve the hardened release as the human owner:
   <!-- run: approve -->
   ```sh
   cub mini approve fx-api-file-proposals/ORDER --yes
   ```

5. As `agy-oncall` (2 AM cold start, zero shared chat), read `fx-api-live` history and propose the surgical forward fix `FX_CACHE_TTL_SEC=15`; approve as the human owner and confirm `FX_POLL_INTERVAL_MS=1000`, `FX_RATE_LIMIT_RPM=10`, `FX_CACHE_TTL_SEC=15`, and `FX_SPREAD_BPS=25`:
   <!-- run: act3 -->
   ```sh
   CUB_CONFIG="$HOME/.confighub-agent-agy-oncall" CUB_CONTEXT=agy-oncall \
     cub revision list --space fx-api-live app
   CUB_CONFIG="$HOME/.confighub-agent-agy-oncall" CUB_CONTEXT=agy-oncall \
     cub mini set fx-api FX_CACHE_TTL_SEC=15 --variant live \
     --change-desc "agy-oncall: fix HTTP 429s by caching vendor FX quotes 15s without reverting 1s ticker or touching FX_SPREAD_BPS"
   ```

## Agent

Follow [`examples/skills/confighub-ops/SKILL.md`](../skills/confighub-ops/SKILL.md): always use your assigned `CUB_CONFIG` and `CUB_CONTEXT`, inspect `cub revision list` before editing, attach a clear `--change-desc` to every change, and never attempt to approve production changes yourself.

## Testing

The full three-agent handoff ran end to end against a real ConfigHub v0.11.1 hub on macOS arm64 with three separate scoped service accounts (`claude-dev`, `codex-ops`, `agy-oncall`). `codex-ops` attempting to approve a live change order was refused by ConfigHub (`only a person named as an approver for production can approve this change, and codex-ops is not one. Nothing was changed`). After `agy-oncall`'s surgical fix and human approval, `fx-api-live` held `FX_POLL_INTERVAL_MS=1000`, `FX_RATE_LIMIT_RPM=10`, `FX_CACHE_TTL_SEC=15`, and `FX_SPREAD_BPS=25`.

<!-- agent-task: act1 -->
> As `claude-dev`, set `FX_POLL_INTERVAL_MS=1000` in staging with a reason.
<!-- agent-check act1: cub unit data --space fx-api-staging app | grep -Fx "FX_POLL_INTERVAL_MS=1000" -->
<!-- agent-task: act3 -->
> As `agy-oncall`, inspect `fx-api-live` history and propose `FX_CACHE_TTL_SEC=15` without reverting the ticker or touching `FX_SPREAD_BPS`.
<!-- agent-check act3: cub unit data --space fx-api-live app | grep -Fx "FX_SPREAD_BPS=25" -->
<!-- next-step boundary=same-tier: self-host the hub for your team | Ready to run this shared operational memory in your cluster behind corporate SSO? -->
<!-- arms: a -->

This proves: three different AI agents with zero shared chat history can hand off, harden, and recover a production service safely using ConfigHub as their shared operational memory, with human approval enforced on every production change.

<!-- results:begin -->

<details><summary>Test results</summary>

26 November 2026, on published `confighub-mini-0.11.1-mini.41` (macOS arm64). Three scoped service accounts (`claude-dev`, `codex-ops`, `agy-oncall`) ran Acts 1–3 with zero shared chat history. `codex-ops` self-approval was refused by ConfigHub; human owner approved hardened release and `agy-oncall`'s surgical `FX_CACHE_TTL_SEC=15` fix; final `fx-api-live` held `FX_POLL_INTERVAL_MS=1000`, `FX_RATE_LIMIT_RPM=10`, `FX_CACHE_TTL_SEC=15`, and `FX_SPREAD_BPS=25`.

</details>

<!-- results:end -->

</details>
