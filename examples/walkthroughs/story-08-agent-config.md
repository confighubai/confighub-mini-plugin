<!-- walkthrough
id: story-08-agent-config
starts_with: mini
story: "8. An agent's own configuration: "Give every team the assistant, and let each keep what it changed""
needs: [confighub mini package]
budget_seconds: 90
-->
# One AI assistant for every team, each team keeping its own choices

For a platform team that gives several teams the same AI assistant. The assistant's definition is a small settings file: its model, its prompt, its tools and its limits. Support and Research each make it their own, with a reason for each change. When the platform team ships a new version, each team takes it and keeps what it chose, and Research records the evaluation that explains why it stays on the older model.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)). No Docker, no cluster and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it.

### Steps

1. Say where the unpacked package is:

   <!-- run: package files -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   ```

2. Set up a terminal for this walkthrough. `CUB_CONFIG` gives it a `cub` configuration of its own, so your own `cub` settings are not touched:

   <!-- run: setup -->
   ```sh
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

3. Copy the example into a folder of your own:

   <!-- run: copy files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/agent-config" ~/walkthrough/ && cd ~/walkthrough/agent-config
   ```

4. Start a hub, and put the platform team's assistant in it. It goes in as the *base*, `support-assistant-base`, the copy that takes each new version:

   <!-- run: assistant-hub -->
   ```sh
   cub mini install --name agents --use
   cub mini upload support-assistant.yaml
   ```

5. Give each team its own copy of it, a *variant* of the base:

   <!-- run: assistant-teams -->
   ```sh
   cub variant create support support-assistant-base
   cub variant create research support-assistant-base
   ```

6. Each team makes the assistant its own, with its reasons. Support lets it read customers' tickets. Research raises its token budget, and pins the model it already runs: setting a value a copy already has keeps it, so the next version will not overwrite it.

   <!-- run: assistant-changes -->
   ```sh
   cub mini set support-assistant tools.read-tickets=true --variant support \
     --change-desc "Support answers from the customer's tickets"
   cub mini set support-assistant model=large-2026-09 --variant research \
     --change-desc "Our evaluation of the newer model on our questions is not finished"
   cub mini set support-assistant limits.maxTokensPerDay=6000000 --variant research \
     --change-desc "Research runs long analyses; budget agreed with finance"
   ```

   ```text
   …
   support-assistant-research already has model=large-2026-09. A later version of what support-assistant-research is made from will not overwrite this value now.
   …
   ```

7. The platform team's next version arrives: a newer model, a tool that can open changes, and more tool calls per task. Put it into the base. Before anything changes, each team is shown what it would take and what it keeps. It asks whether to take it; answer `n` for now, or press Enter.

   <!-- run: assistant-next any-order -->
   ```sh
   cub mini upload next/support-assistant.yaml --component support-assistant
   ```

   ```text
   support-assistant-support
   changes model large-2026-09 → large-2026-11
   changes tools.open-change false → true
   support-assistant-research
   you keep model yours: large-2026-09 (offered: large-2026-11)
   Nothing running has changed. To take it later:
   ```

8. Both teams take it:

   <!-- run: assistant-take -->
   ```sh
   cub mini promote support-assistant-support support-assistant-research \
     --change-desc "Take the platform team's new support assistant"
   ```

   ```text
   …
   Done. Each copy kept its own values.
   ```

9. Research records its evaluation of the newer model, against the version it judged. `--reject` records a fail; ConfigHub calls a verdict like this an *attestation*:

   <!-- run: assistant-evaluate -->
   ```sh
   cub attestation create --space support-assistant-research --type Evaluation --reject \
     --note "large-2026-11 on our research questions: 2 of 50 cite papers that do not exist"
   ```

   ```text
   Recorded fail Evaluation attestation ID in support-assistant-research, covering 1 revision(s)
   ```

10. Ask which team runs which model, and why:

   <!-- run: assistant-why -->
   ```sh
   cub unit data support-assistant --space support-assistant-support | grep -E '^model|read-tickets'
   cub unit data support-assistant --space support-assistant-research | grep -E '^model|open-change|maxTokens'
   ```

   ```text
   model: large-2026-11
   read-tickets: true # Support answers from the customer's tickets
   model: large-2026-09 # Our evaluation of the newer model on our questions is not finished
   open-change: true
   maxTokensPerDay: 6000000 # Research runs long analyses; budget agreed with finance
   ```

### Undo it

This removes the hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --name agents --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind. While it ran, both teams had the new assistant, Support on the newer model, Research on its own with the reason beside it, and the evaluation that explains the difference kept next to the version it judged. The full story adds Support's passing evaluation, and evaluations that must pass before production, which are not built yet.

## Agent

For an AI agent doing this for a person.

- **The request:** "Give Support and Research their own copy of our support assistant. Support may read customers' tickets because it answers from them. Research keeps model large-2026-09 because its evaluation of the newer model is not finished. Then take the platform team's next version for both, and record that Research's evaluation of large-2026-11 failed: 2 of 50 answers cite papers that do not exist."
- **What to run:** the Human steps 4 to 10, from a copy of `$MINI/examples/agent-config`, with the person's reasons as each `--change-desc`. Show the person the preview before taking the version. End by telling them which model each team runs and why.
- **Never:** edit `support-assistant.yaml` by hand to keep Research's model; put an API key in the definition; record an evaluation the person did not give you.
- **Done when:** Support's copy runs `large-2026-11` with ticket reading on, Research's runs `large-2026-09` with its reason and the new tool, and Research has a failed Evaluation attestation.

## Testing

The scripted run follows the Human steps on a hub of its own and compares the quoted output. A correct agent result is the two teams' copies as above, with Research's failed evaluation recorded. Without a hub, the equivalent is two files, one for each team, with those values. The checks below can be run by hand after the steps:

This proves: stored. Each team's definition, its reasons and the evaluation are in a hub on this computer; no assistant runs from them. The next step this aims to win: adding the next team to the same hub.

<!-- agent-task: assistant -->
> Our support assistant's definition is support-assistant.yaml in this folder, and the platform team's next version is in next/. Give Support and Research their own copy, named support and research. Support may read customers' tickets because it answers from them. Research keeps model large-2026-09 because its evaluation of the newer model is not finished. Then take the next version for both, and record that Research's evaluation of large-2026-11 failed: 2 of 50 answers cite papers that do not exist.

<!-- agent-check assistant: r=$(cub unit data support-assistant --space support-assistant-research) && s=$(cub unit data support-assistant --space support-assistant-support) && echo "$r" | grep -q '^model: large-2026-09 #' && echo "$r" | grep -q 'open-change: true' && echo "$s" | grep -q '^model: large-2026-11' && echo "$s" | grep -q 'read-tickets: true' && cub attestation list --space support-assistant-research | grep -q 'Evaluation *Fail' -->
<!-- agent-check-a assistant: r=$(grep -rl --include='*.yaml' '^model: large-2026-09' . | xargs grep -l 'open-change: true' | head -1) && s=$(grep -rl --include='*.yaml' '^model: large-2026-11' . | xargs grep -l 'read-tickets: true' | head -1) && [ -n "$r" ] && [ -n "$s" ] -->
<!-- arms: a,b -->
<!-- next-step when "recorded": give a third team the assistant | Give a third team its own copy of the assistant, with the same next version and its own reasons? -->

```sh
cub unit data support-assistant --space support-assistant-research | grep -E '^model|open-change'
cub unit data support-assistant --space support-assistant-support | grep -E '^model|read-tickets'
cub attestation list --space support-assistant-research
```
