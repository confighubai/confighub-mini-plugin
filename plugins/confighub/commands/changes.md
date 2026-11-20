---
description: What agents changed in this folder's configuration, and why
disable-model-invocation: true
allowed-tools: Bash("${CLAUDE_PLUGIN_ROOT}/bin/confighub":*)
---

!`"${CLAUDE_PLUGIN_ROOT}/bin/confighub" mini changes --summary`

Show the record above verbatim in a code block. Follow it with one next step for the person to try in this chat.

If it lists a setting, name it in a suggested question: “Before I change SETTING back, where is it used, and what was the reason for changing it?” Use only the setting name in the suggestion. If there are no recorded settings, suggest asking for an ordinary settings edit with a reason, then asking a fresh chat in the same folder why it changed. Do not run the suggestion or change any files.
