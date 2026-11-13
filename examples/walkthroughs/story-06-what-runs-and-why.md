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

An unpacked confighub mini package, 0.10.7-mini.24 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, and internet access to render NVIDIA's published GPU Operator chart. No cluster, no Docker and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool, and `cub mini` the commands confighub mini adds to it.

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

This proves: stored. The answers are read from what a hub on this computer holds; no customer's cluster is read, and nothing is delivered.

<!-- agent-task: inventory -->
> Our GPU platform is rendered in this folder (given/), and ./customers loads our three customers' copies, Birch, Cedar and Elm, into a hub. Which customers differ from the platform we gave them, how, do we know why, and does any break our rule that images come only from nvcr.io or registry.k8s.io? Do not change anything. Write the answer to answer.md.

<!-- agent-check inventory: f=$(find . -name answer.md | head -1) && grep -qi 'birch' "$f" && grep -q 'registry.dev.example' "$f" && grep -q '580.95.05' "$f" && grep -qi '1Gi' "$f" && cub function get --space gpu-operator-birch --unit gpu-operator --show values get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image' | grep -q 'registry.dev.example' -->
<!-- agent-check-a inventory: f=$(find . -name answer.md | head -1) && grep -qi 'birch' "$f" && grep -q 'registry.dev.example' "$f" && grep -q '580.95.05' "$f" && grep -qi '1Gi' "$f" -->
<!-- agent-tools: ./customers -->
<!-- arms: a,b -->

```sh
cat answer.md
cub function get --space gpu-operator-birch --unit gpu-operator --show values \
  get-string-path apps/v1/Deployment 'spec.template.spec.containers.?name=gpu-operator.image'
```
