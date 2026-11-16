---
description: Start this app from another app in the hub, keeping the values this app's own files set; with no app named, list them
argument-hint: "[APP [FOLDER]]"
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini start-from $ARGUMENTS 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
