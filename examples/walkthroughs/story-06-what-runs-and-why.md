<!-- walkthrough
id: story-06-what-runs-and-why
starts_with: mini
story: "6. Ivan: "Show me what is actually running, and who changed what""
needs: [confighub mini package, helm, python3, internet access to render the chart]
budget_seconds: 150
-->
# Which customer changed what, whether anyone said why, and who breaks the rules

For a platform engineer whose customers each run a changed copy of the platform he gave them. Before the next version ships, Ivan wants an inventory: which driver each customer runs, what each one changed and whether a reason was recorded, and whether anyone breaks the rule that images come only from NVIDIA's or Kubernetes' registry. Each answer is one command across every customer at once, with no script of his own.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, and internet access to render NVIDIA's published GPU Operator chart. No cluster, no Docker and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it.

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

3. Copy the example, and render the platform as it was given to customers:

   <!-- run: copy files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/gpu-platform" ~/walkthrough/ && cd ~/walkthrough/gpu-platform
   ./render
   ```

4. Start a hub, and load the platform into it as the *base*, the one starting point every customer is compared with:

   <!-- run: inventory-hub -->
   ```sh
   cub mini install --name ivan --use
   cub mini upload given/gpu-operator --namespace gpu-operator
   ```

5. Load the three customers, Birch, Cedar and Elm. Each is a *variant*, the customer's own copy of the base, changed the way real ones are:

   <!-- run: inventory-customers -->
   ```sh
   ./customers
   ```

   ```text
   Three customers: gpu-operator-birch, gpu-operator-cedar, gpu-operator-elm
   ```

6. Ask which driver each customer runs. `--space '*'` asks every copy at once. Cedar runs 580.95.05, where the platform and the others have 580.105.08:

   <!-- run: inventory-driver any-order -->
   ```sh
   cub function get --space '*' --unit cluster-policy-clusterpolicy \
     get-string-path nvidia.com/v1/ClusterPolicy spec.driver.version
   ```

   ```text
   Function(s) succeeded on unit gpu-operator-cedar/cluster-policy-clusterpolicy (ID)
   Value: 580.95.05 Path: spec.driver.version Resource: /cluster-policy Type: nvidia.com/v1/ClusterPolicy
   Value: 580.105.08 Path: spec.driver.version Resource: /cluster-policy Type: nvidia.com/v1/ClusterPolicy
   ```

7. Check the image rule across every customer. Only Birch breaks it, with a development image someone left behind:

   <!-- run: inventory-rule -->
   ```sh
   cub function vet --space '*' -- vet-images '{"AllowRegexp":"^(nvcr\\.io|registry\\.k8s\\.io)/"}' \
     | grep -A2 'Passed: false'
   ```

   ```text
   Passed: false Function: vet-images
   Attributes:
   Value: registry.dev.example/gpu-operator:v25.10.1-debug Path: spec.template.spec.containers.?name=gpu-operator.image Resource: gpu-operator/gpu-operator Type: apps/v1/Deployment
   ```

8. Ask what each customer changed, and why. This writes every copy out as files, with the list of changes in `CHANGES.md`; it changes nothing in the hub. Where nobody recorded a reason, the list shows only the command that made the change:

   <!-- run: inventory-changes -->
   ```sh
   cub mini copy gpu-operator --to-dir inventory
   grep -E 'birch|cedar|elm' inventory/CHANGES.md | cut -d'|' -f2,4,5,6
   ```

   ```text
   …
   gpu-operator-birch | `spec.template.spec.containers.?name=gpu-operator.image` | `registry.dev.example/gpu-operator:v25.10.1-debug` | Functions: set-string-path
   gpu-operator-cedar | `spec.driver.version` | `580.95.05` | Our nodes are certified with driver 580.95.05
   gpu-operator-elm | `spec.template.spec.containers.?name=gpu-operator.resources.limits.memory` | `1Gi` | Functions: set-string-path
   ```

9. Write down what you found, for whoever ships the next version:

   <!-- run: inventory-answer -->
   ```sh
   cat > answer.md <<'NOTE'
   - Birch: runs registry.dev.example/gpu-operator:v25.10.1-debug, which breaks the image rule. No reason recorded.
   - Cedar: driver 580.95.05. Reason: "Our nodes are certified with driver 580.95.05". Kept through the next version.
   - Elm: operator memory limit 1Gi. No reason recorded.
   NOTE
   ```

### Undo it

This removes the hub with everything in it, and the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cub mini uninstall --name ivan --delete-data
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

A list you can trust, and nothing left behind: Birch breaks the image rule and nobody said why; Cedar changed its driver on purpose and said why, and the hub keeps it through the next version; Elm raised its memory limit and nobody said why. Those are the three conversations to have before the next version ships. The full story adds an agent that answers the same question on a key that can read the hub and change nothing, and a saved question a new session finds by itself.

## Agent

For an AI agent doing this for a person.

- **The request:** "Which of our customers differ from the platform we gave them, how, do we know why, and does any break our rule that images come only from nvcr.io or registry.k8s.io? Write the answer to answer.md."
- **What to run:** the Human steps 4 to 8, from a copy of `$MINI/examples/gpu-platform`. Prefer the one command that checks a rule across every copy (`cub function vet --space '*'`) over reading files one by one. Write `answer.md` with one line for each customer: what differs, whether a reason was recorded, and whether it breaks the rule.
- **Never:** change any customer's configuration; this is a question, not a fix. Do not guess a reason that was not recorded: say "no reason recorded".
- **Done when:** `answer.md` names Birch's debug image as breaking the rule with no reason, Cedar's driver 580.95.05 with its reason, and Elm's 1Gi memory limit with no reason, and the hub still holds Birch's image unchanged.

## Testing

The scripted run follows the Human steps on a hub of its own and compares the quoted output. A correct agent result is an `answer.md` with the three findings, and, where there is a hub, Birch's image left as it was. The checks below can be run by hand after the steps and an answer:

This proves: stored. The answers are read from what a hub on this computer holds; no customer's cluster is read, and nothing is delivered. The next step this aims to win: recording a reason where the list shows none. Tested on the checksum-verified published confighub mini 0.11.1-mini.4 with the plugin 0.87.0, 14 November 2026: environment, local hub, no cluster; approval, no approval step. The plugin says one line at this moment, such as "ConfigHub plugin: inventory/CHANGES.md lists what each copy changed, with the reason where one was given; nothing in the hub changed." The next-step line names words from that line.

<!-- agent-task: inventory -->
> Our GPU platform is rendered in this folder (given/), and ./customers loads our three customers' copies, Birch, Cedar and Elm, into a hub. Which customers differ from the platform we gave them, how, do we know why, and does any break our rule that images come only from nvcr.io or registry.k8s.io? Do not change anything. Write the answer to answer.md.

<!-- agent-check inventory: f=$(find . -name answer.md | head -1) && grep -qi 'birch' "$f" && grep -q 'registry.dev.example' "$f" && grep -q '580.95.05' "$f" && grep -qi '1Gi' "$f" && cub function get --space gpu-operator-birch --unit gpu-operator --show values get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image' | grep -q 'registry.dev.example' -->
<!-- agent-check-a inventory: f=$(find . -name answer.md | head -1) && grep -qi 'birch' "$f" && grep -q 'registry.dev.example' "$f" && grep -q '580.95.05' "$f" && grep -qi '1Gi' "$f" -->
<!-- agent-tools: ./customers -->
<!-- arms: a,b -->
<!-- next-step boundary=same-tier when "lists what each copy changed": record the missing reasons | Ask Birch and Elm why they changed what they did, and record it beside the change? -->

```sh
cat answer.md
cub function get --space gpu-operator-birch --unit gpu-operator --show values \
  get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image'
```

<!-- results:begin -->

Results, 14 November 2026, confighub mini 0.11.1-mini.4. Figures from this page's own test runs, shown here for whoever checks the page; they are not a promise.

- Scripted run: passed, 41 seconds for the steps, within the page's budget of 150.
- Agent runs (on confighub mini 0.11.1-mini.4, 14 November 2026): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| b | claude-opus-5-5 | 3/3 | 68.5 | $0.226 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 57.5 | $0.119 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Ask Birch and Elm why they changed what they did, and record it beside the change?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("lists what each copy changed"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| b | claude-opus-5-5 | 30 | 100% | 100% | 17% | 83% | 30% |
| b | claude-sonnet-5-5 | 30 | 100% | 100% | 7% | 93% | 53% |

- Agent runs (on confighub mini 0.11.1-mini.2, 14 November 2026): a pilot, 3 runs per arm on each of claude-sonnet-5-5, claude-opus-5-5. Arms: a is ordinary tools only; b is the plugin, confighub mini and this page as reading.

| Arm | Model | Checks passed | Median seconds | Median cost | Commands left for the person (median) |
|---|---|---|---|---|---|
| a | claude-opus-5-5 | 2/3 | 56.5 | $0.326 | 0 |
| b | claude-opus-5-5 | 3/3 | 77.0 | $0.233 | 0 |
| a | claude-sonnet-5-5 | 3/3 | 20.3 | $0.099 | 0 |
| b | claude-sonnet-5-5 | 3/3 | 56.3 | $0.114 | 0 |

No agent approved or refused a change to production.

Simulated persons, not people: 10 per run, each a claude-haiku-5-5 model playing one of ten fixed personas, reading only what a person would see. The next step they were offered: "Ask the same three questions again next week, across every customer, and see what changed since?"

The plugin offers it once, after the answer at whose end it showed the moment the offer names ("what your agents changed"). Offered is the share of persons it was shown to; want it now and later are over them.

| Arm | Model | Persons | Offered | Noticed | Want the next step now | Later | In the way |
|---|---|---|---|---|---|---|---|
| a | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 73% |
| b | claude-opus-5-5 | 30 | 0% | 100% | n/a | n/a | 37% |
| a | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 93% |
| b | claude-sonnet-5-5 | 30 | 0% | 100% | n/a | n/a | 47% |

<!-- results:end -->
