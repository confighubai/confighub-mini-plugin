---
description: Give this app a staging and a production copy of its settings, with production behind your approval
argument-hint: "[FOLDER] [--heroku APP | --unikraft SERVICE]"
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini staging $ARGUMENTS 2>&1`

Show the person the output above exactly as it is, in a code block, and add nothing to it.
