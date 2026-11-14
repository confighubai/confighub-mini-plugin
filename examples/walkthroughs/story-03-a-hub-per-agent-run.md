<!-- walkthrough
id: story-03-a-hub-per-agent-run
starts_with: mini
story: "3. Ivan's agents: "Give each run a hub of its own, and throw it away afterwards""
needs: [confighub mini package, macOS, helm, python3, internet access to render the chart]
budget_seconds: 300
-->
# A hub of its own for each agent run, thrown away afterwards

For a team that lets coding agents work on its platform but does not want an agent anywhere near the team's own hub. The team writes its work to one file. An agent's run gets that file and a sandbox, and its first command starts a hub of its own inside the sandbox. The agent makes its fix there, writes it out for a person to review, and the hub is deleted with the run. The team's hub never changes until a person takes the result.

## Human

### What you need

A Mac, for the sandbox (it uses macOS's `sandbox-exec`), an unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, and internet access to render NVIDIA's published GPU Operator chart. No Docker, no cluster and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it. A *sandbox* here is a folder and a `cub` configuration of the run's own, in which every command can reach only hubs on this machine and write only its own folder.

### Steps

1. Set up a terminal for this walkthrough. `CUB_CONFIG` gives it a `cub` configuration of its own, so your own `cub` settings are not touched; a hub's files must be under your home folder. `CONFIGHUB_MINI_PACKAGE` tells the example's scripts where the package is:

   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   export CONFIGHUB_MINI_PACKAGE="$MINI"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

2. Play the team: render the GPU platform, start the team's hub, and load the platform with three customers, Birch, Cedar and Elm. Birch runs a development image someone left behind.

   <!-- run: team -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/gpu-platform" ~/walkthrough/ && cd ~/walkthrough/gpu-platform
   ./render
   cub mini install --name team --use
   cub mini upload given/gpu-operator --namespace gpu-operator
   ./customers
   ```

3. The team writes its work to one file. That file is all an agent run gets: no key to the team's hub.

   <!-- run: file -->
   ```sh
   cub mini copy gpu-operator --to-file platform.tar.gz
   ```

   ```text
   …
   To take it into another hub:
   cub mini copy --from-file platform.tar.gz
   ```

4. Give the run's sandbox the `cub mini` commands. They are linked to the package, not copied, so the sandbox's configuration stays a few kilobytes:

   <!-- run: sandbox -->
   ```sh
   cub mini install-plugin sandbox-a
   ```

5. Now play the agent. Every command goes through `./sandbox`, which lets it reach only hubs on this machine and write only this folder and `sandbox-a`. Its first command loads the file. There is no hub in the sandbox yet, so one starts first:

   <!-- run: fix-load any-order -->
   ```sh
   ./sandbox . sandbox-a cub mini copy --from-file platform.tar.gz gpu-operator
   ```

   ```text
   cub mini: there is no hub here, and cub has only the context it made on first run; starting one, as cub mini install would.
   …
   From now on, changes to it are made in this hub. It comes out again as plain files, with a list of what was changed here and why:
   …
   ```

6. The agent fixes Birch's image in its own hub, with the reason. `--unit gpu-operator` names the one piece of configuration to change; without it, every Deployment in Birch's installation would change:

   <!-- run: fix-set -->
   ```sh
   ./sandbox . sandbox-a cub mini set gpu-operator container-image gpu-operator nvcr.io/nvidia/gpu-operator:v25.10.1 \
     --unit gpu-operator --variant birch \
     --change-desc "Back to the platform image: Birch ran a debug build from registry.dev.example, outside the allowed registries"
   ```

   ```text
   …
   registry.dev.example/gpu-operator:v25.10.1-debug → nvcr.io/nvidia/gpu-operator:v25.10.1
   …
   ```

7. The agent writes Birch's installation out as plain files for a person to review, with the list of what it changed and why in `result/CHANGES.md`, and the run ends: its hub is removed with its data.

   <!-- run: fix-result -->
   ```sh
   ./sandbox . sandbox-a cub mini copy gpu-operator --variant birch --to-dir result
   ./sandbox . sandbox-a cub mini uninstall --delete-data
   ```

   ```text
   Wrote 2 Spaces and 54 Units from this hub to result, with the list in CHANGES.md. Nothing was changed in the hub.
   …
   Removed the hub "mini": its data, its cub context, and the server and database it ran, which no other hub used.
   ```

8. Back as the team: its hub still has Birch's development image, because nobody has taken the agent's result yet. The fix waits in `result/` for a person.

   <!-- run: fix-team-unchanged -->
   ```sh
   cub function get --space gpu-operator-birch --unit gpu-operator --show values \
     get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image'
   ```

   ```text
   registry.dev.example/gpu-operator:v25.10.1-debug
   ```

### Undo it

This removes the team's hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --name team --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind. While it ran, the agent's fix sat in `result/` with its reason, for a person to take or leave, and the team's hub had changed in nothing. The full story adds two agents at once in sandboxes side by side, the result taken back through the team's Git, and the same in CI and in Linux containers; [CI and sandboxes](../../docs/ci-and-sandboxes.md) shows those.

## Agent

For an AI agent doing this for a person. Here the agent is the one in the sandbox.

- **The request:** "Our platform and customers are in platform.tar.gz. One customer's operator image breaks our rule that images come only from nvcr.io or registry.k8s.io. Find it and fix it in a hub of your own, and leave the fix as files for me to review. Don't touch the team's hub."
- **What to run:** every command through `./sandbox . sandbox-a ...`: `cub mini copy --from-file platform.tar.gz gpu-operator` (it starts your hub), `cub function vet --space '*' -- vet-images '{"AllowRegexp":"^(nvcr\\.io|registry\\.k8s\\.io)/"}'` to find it, `cub mini set ... --unit gpu-operator --variant birch --change-desc "<why>"`, `cub mini copy gpu-operator --variant birch --to-dir result`, then `cub mini uninstall --delete-data`. Tell the person where `result/CHANGES.md` is.
- **Never:** run a `cub` command outside `./sandbox`, which would reach the team's hub; change a customer you were not asked to fix; leave the sandbox's hub running.
- **Done when:** `result/CHANGES.md` lists Birch's image with your reason, the sandbox's hub is gone, and the team's hub still has Birch's old image.

## Testing

The scripted run follows the Human steps and compares the quoted output. Arm a, without confighub mini, is not applicable: the team's customers exist only in a hub, and the point is a hub of the run's own. A correct agent result is the fix in `result/CHANGES.md`, no hub left in the sandbox, and the team's hub unchanged. The checks below can be run by hand, from the example's folder, after the steps:

This proves: stored, in a hub of the run's own that was then deleted, with the fix written out as files for review; nothing is delivered. It uses macOS's `sandbox-exec` as the sandbox. The next step this aims to win: making a hub of its own the default for each agent run. Tested on the checksum-verified published confighub mini 0.11.1-mini.2 with the plugin 0.85.0, 14 November 2026: environment, local hub inside macOS sandbox-exec; approval, no approval step.

<!-- agent-task: fix -->
> The team's GPU platform and its three customers are in ./platform.tar.gz. One customer's operator image breaks our rule that images come only from nvcr.io or registry.k8s.io. Find it and fix it in a hub of your own, running every command through ./sandbox with the sandbox configuration ./sandbox-a (./sandbox . sandbox-a COMMAND), and leave the fix as files in ./result for me to review. Don't touch the team's hub, and don't leave your hub running.

<!-- agent-check fix: r=$(find . -path '*result/CHANGES.md' | head -1) && grep 'gpu-operator-birch' "$r" | grep -q 'nvcr.io/nvidia/gpu-operator:v25.10.1' && ! ls -d "$(dirname "$(dirname "$r")")"/sandbox-a/servers/*/ >/dev/null 2>&1 && cub function get --space gpu-operator-birch --unit gpu-operator --show values get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image' | grep -q 'registry.dev.example' -->
<!-- agent-tools: ./sandbox -->
<!-- arms: b -->
<!-- next-step when "recorded": a hub of its own for every agent run | Give every agent run its own hub from the team's file, so none of them ever holds a key to the team's hub? -->

```sh
grep birch result/CHANGES.md
ls sandbox-a/servers 2>/dev/null || echo "no hub left in the sandbox"
cub function get --space gpu-operator-birch --unit gpu-operator --show values \
  get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image'
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.2. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 80 seconds for the steps, within the page's budget of 300.
- Agent runs: a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading; c is the plugin and confighub mini, without this page.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 3/3 | 101.8 | $0.295 | 0 |
| c | claude-opus-5-5 | 2/3 | 149.3 | $0.669 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 60.8 | $0.108 | 0 |
| c | claude-sonnet-5-5 | 3/3 | 129.5 | $0.33 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Give every agent run its own hub from the team's file, so none of them ever holds a key to the team's hub?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("recorded"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 60% |
| c | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 77% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 27% |
| c | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 67% |

<!-- results:end -->
