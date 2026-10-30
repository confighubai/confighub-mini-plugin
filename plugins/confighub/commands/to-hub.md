---
description: Copy what agents changed here, and why, into the ConfigHub your cub is signed in to
disable-model-invocation: true
argument-hint: "[--yes] [--context NAME]"
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini to-hub $ARGUMENTS 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
