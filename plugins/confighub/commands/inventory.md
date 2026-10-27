---
description: What this repository deploys, the values that differ between environments, and the values agents changed
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini inventory 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
