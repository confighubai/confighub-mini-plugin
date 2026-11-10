# Ordinary app requests and visible ConfigHub activity

10 November 2026. Real Claude Code and Codex sessions, with a private hub configuration
and scoped proposer key per app. The server was ConfigHub v0.10.7; the candidate client
was built over a verified mini.17 package. Final release checks run separately on the
published package. This is engineering evidence, not outside-user acceptance.

## What was asked

No prompt named a skill, ConfigHub command or roadmap ID. The app's README and
`.confighub-app` described its existing configuration. Requests asked for an isolated
memory change, production delivery, or another app with its own port. Models were
`gpt-6.1-sol`, `gpt-6-sol`, Claude Sonnet 5.5 and Opus 5.5, two rounds each.

The setup's baseline approvals were scripted before each agent started. The agent could
not approve its own proposal or read the owner's configuration. No production service
was connected: these checks concern stored settings and their exact live revision.

## Results and corrections

| Evaluation | Task | Safety | Attribution |
|---|---|---|---|
| Initial Codex, 16 sessions | 16/16 | 16/16 | 15/16 |
| Initial Claude, 16 sessions | 14/16 | 16/16 | 16/16, including native client notices |
| Revised Codex, tries and reuse, 8 sessions | 8/8 | 8/8 | 8/8 |
| Revised Claude, tries and reuse, 8 sessions | 7/8 | 8/8 | 8/8 |
| Claude absolute-path permission recheck, 2 sessions | 2/2 | 2/2 | 2/2 |

The one revised Claude task stopped at its native Bash approval: the test allowed
`cub ...` but not the same executable's absolute path. Preapproving that exact packaged
path fixed the fixture; it did not broaden the hub key or remove filesystem protection.
Both reruns completed. Earlier failed results are retained, not replaced with successes.

Two initial Opus reuse sessions stopped at instructions without preparing files. The
workflow now prepares a new app inside a writable workspace when the folder above it is
outside the sandbox, names its actual location, and leaves placement and hub adoption
explicitly pending. Both revised Opus reuse sessions prepared the requested files.

One initial Codex session omitted a clear activity line in plain CLI output. The workflow
now uses the same brief ConfigHub line for skill use and action attribution. Hook notices
remain the fallback; native informational notices count separately from assistant text.
Quoted skill or tool output counts as neither. Recent visible commentary suppresses the
duplicate hook line when its transcript is available. CLI rendering still varies by client.

## Recording without a hub, and a remembered decline

Eight three-session paths across those four models built an ordinary Python function,
asked not to offer a hub again, then changed the code in a fresh session. All eight
completed the code and kept recording without starting a hub. Seven initially saved the
plugin preference; one Sonnet session saved it only in Claude's native memory.

The hook now recognises common direct project declines itself. Two Sonnet paths were
rerun (six sessions); both saved the plugin preference and kept it in the fresh session.
A generic no, quoted example or instruction not to install yet is not a project preference.
Other explicit wording can use `changes --hub-suggestions off`; preferences are editable
choices outside the protected signed record.

## Product defects caught

- A try made from staging was absent from direct-base-only key assignment. The regression
  failed before the fix. Connected descendants are now assigned while orphans stay out;
  gating a try revokes its write rights. An unreadable workflow is not treated as no gate.
- A Git checkout could keep using an old expanded executable after pulling new compressed
  programs. The regression failed before the fix; unchanged programs still stay cached.
- Codex setup installs the shared workflow and reference, preserves personal hooks, refuses
  to overwrite edited skills, and retains those edits when removing its hooks and program.

## Explicit setup and release-check corrections

The first full release candidate exposed a cold-start regression: a Claude session asked
explicitly to build an app using ConfigHub made plain files and offered setup instead.
The workflow now treats that request as the setup choice already made. Focused Sonnet
and Opus reruns each completed the app and hub setup (3/3 assertions per model).

The same candidate exposed two stale checks. A fresh checkout deliberately receives
per-value reasons, not raw requests; the fixture now requests reasons before committing
and checks the causal explanation. Both models passed all five assertions. The interactive
reason check now checks the two displayed value explanations and their stored reasons,
rather than an optional heading. It permits the documented opt-in Stop-hook request once;
the Sonnet rerun passed all three assertions. Raw requests were not added to shared records.

A Codex cold-start probe in workspace-write mode could not download or start a local hub:
its native sandbox denied network and local service ports. It reported setup pending and
completed the files without claiming adoption. Owner setup needs those native permissions;
that probe is not counted as successful setup or as a scoped-key safety measurement.

## Reproduce and limits

```sh
CONFIGHUB_MINI_PACKAGE=/path/to/package examples/check-natural-workflow /path/to/new-record
CONFIGHUB_MINI_PACKAGE=/path/to/package examples/check-natural-workflow /path/to/claude-record --client claude
```

Each defaults to two models and two rounds. The generated launchers and Claude test rules
provide ordinary tool permission; ConfigHub approval remains the owner's separate action.
Go tests cover preference parsing/persistence, secret-free notices, duplicate suppression,
permission preservation, skill ownership/removal, key assignment and update freshness.

The structured [summary](summary.json) preserves the separate scores. Raw transcripts,
original and corrected evaluators, before/after regressions and checksums are archived in
`~/code/_archives/confighub-mini/2026-11-10/agent-workflow-0.79.9` after release cleanup.

Creating a new try/app or granting CI access still needs owner setup on a restricted key.
These runs do not prove running-service delivery, native chat approval, CI/hub migration,
free two-person cloud sharing, generated-manifest reason transfer or unaided human use.
