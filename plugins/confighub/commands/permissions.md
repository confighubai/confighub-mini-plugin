---
description: What your settings files allow agents to run, which rules were used, and a narrower set
disable-model-invocation: true
argument-hint: "[--read | --apply | --apply --yes | --undo]"
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini permissions $ARGUMENTS 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
