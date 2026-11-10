# Ordinary app requests and ConfigHub activity notices

10 November 2026. Engineering checks with real Claude Code and Codex sessions, a
ConfigHub v0.10.7 server, isolated configurations and scoped app keys. These checks
use stored settings; no production service was connected and no person approved a
production change during an agent session.

Requests named development goals, not ConfigHub commands or skills. The app's existing
configuration was described by its README and `.confighub-app`.

| Cohort | Task completed | Live values and revision protected | Attribution |
|---|---|---|---|
| Initial Codex, two models | 16/16 | 16/16 | 15/16 |
| Initial Claude, two models | 14/16 | 16/16 | 16/16 |
| Revised Codex: tries and reuse | 8/8 | 8/8 | 8/8 |
| Revised Claude: tries and reuse | 7/8 | 8/8 | 8/8 |
| Claude native-permission recheck | 2/2 | 2/2 | 2/2 |

The revised Claude task that stopped needed native Bash approval for the packaged
executable's absolute path. The fixture had preapproved only `cub ...`. Preapproving
the same executable by its full path made both reruns complete; hub rights and filesystem
protection stayed in place. Native tool permission is separate from ConfigHub approval.

Two early reuse sessions only supplied commands. The revised workflow prepares files in
a writable workspace, reports their actual location, and leaves owner adoption explicitly
pending. A file copy does not establish a pattern link. Notice scoring accepts assistant
commentary or a typed native informational notice, and excludes quoted tool/skill text.

Eight three-session paths built ordinary code, declined hub offers and continued in a
fresh session without starting a hub. One Sonnet path initially saved the decline only in
Claude memory. After direct project declines were handled by the hook, both Sonnet paths
were rerun and saved the plugin preference. Code and recording continued in every path.
The [structured summary](summary.json) retains the earlier results separately.

Go regressions cover secret-free notices, preserving permission decisions, duplicate
suppression, project preferences, skill installation/removal and checkout update freshness.
A connected-try regression failed before key assignment was fixed: a try made from staging
is now included without granting live writes; putting the try behind approval revokes writes.
Unknown approval requirements do not grant write access.

This does not prove unaided human use, running-service delivery, authenticated chat
approval, a CI/hub migration or free two-person cloud sharing. See the [workflow guide](../../../agent-workflow.md)
and [client capability matrix](../../../how-it-works.md#client-capabilities).
