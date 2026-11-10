# Codex MCP calls in the record and release check

On macOS ARM64 with Codex CLI 0.163.0, twelve real sessions on gpt-6.1-sol and gpt-6-sol passed [35 checks](result.json). A local MCP stdio server stores fixture notes in disposable SQLite. Four ordinary writes reached the server and were recorded; four at ask were refused before the write call; two server errors made no database change; two controls using the old ask reply permitted writes and were rejected by the ask judge. This is a transport and hook test, not a hosted database, payments integration, outside user or human approval.

Update the hooks after upgrading:

```sh
/path/to/plugins/confighub/bin/confighub mini codex-setup
```

Review changed definitions with `/hooks` in Codex. Existing custom hooks stay in place; older ConfigHub definitions are replaced rather than duplicated.

At log, completed MCP reads and writes enter the ordinary record, with their server, arguments and request. At ask, the adapter refuses changing MCP calls and supported shell-file undos with an explanation: it cannot request that approval prompt in this client. A refusal does not permit a later retry. Claude Code retains its existing prompt behavior.

To reproduce:

```sh
python3 docs/runs/2026-11-09/codex-mcp/check-codex-mcp /path/to/plugins/confighub /new/output/folder --legacy-ask-control
```

The check defaults to two rounds at log and ask on each model, plus an error case. The optional flag adds the two unsafe controls. Each run has its own configuration, database and authentication link; nothing in the personal configuration changes. The fixture tools alone receive native approval, so the client’s own approval policy cannot mask a broken plugin guard. Filesystem sandboxing remains workspace-write. Calls and database state are checked independently of the agent’s answer. All temporary homes, links and fixture files are removed. The standard release check also rejects a client that only says done or exits unsuccessfully, and any MCP-check failure blocks publication.

The [official hook contract](https://learn.chatgpt.com/docs/hooks#pretooluse) describes the unsupported ask reply; [per-tool native approval](https://learn.chatgpt.com/docs/config-file/config-reference) is independent of this plugin. These tests use the CLI setup, not native desktop plugin installation. The twelve candidate sessions preceded a final help-text edit; the release profile checks its final programs separately.

Limits: Codex apply_patch edits are recorded afterwards and are not held before an undo. In these Codex 0.163 error cases, no completion callback reached the configured hooks, so failed calls are missing from the plugin’s structured command record; use the native session transcript for those attempts. If a client reports an error result, it is marked failed and omitted from applied changes. Native approval in the coding-agent chat, failed-call callbacks, real payment/database providers and semantic-repeat evaluation in Codex remain open.
