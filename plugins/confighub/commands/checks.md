---
description: How much the plugin does about agents' MCP calls here, from nothing to asking you first
disable-model-invocation: true
argument-hint: "[off | log | warn | repeats | ask]"
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini checks $ARGUMENTS 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
