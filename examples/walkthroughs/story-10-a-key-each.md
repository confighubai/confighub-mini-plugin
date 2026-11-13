<!-- walkthrough
id: story-10-a-key-each
starts_with: mini
story: "10. Each person on a key of their own, and moving up to the organization's ConfigHub"
needs: [confighub mini package, helm, python3, openssl, internet access to render the chart]
budget_seconds: 150
-->
# Three people, a key each, and everything else refused

For anyone who has to let someone else into their configuration for one job, and out again. Three parties work on one platform: Ivan's team provides it, a customer runs it, and Dan comes in to fix it. Each makes a key of their own and sends only its public half, each is given only what their part needs, and each is refused the rest. When Dan leaves, his key stops working, and the record still names him.

## Human

### What you need

An unpacked confighub mini package, 0.11.1-mini.2 or later ([installing confighub mini](../../docs/install-mini.md#install-by-hand-without-the-plugin)), `helm`, `python3`, `openssl`, and internet access to render NVIDIA's published GPU Operator chart. No cluster, no Docker and no account. A *hub* is ConfigHub running on your computer; `cub` is ConfigHub's command-line tool. A *key* here is a private key a person signs in with; its *public half* is the part that can be sent to others.

### Steps

1. Set up a terminal for this walkthrough. `CONFIGHUB_MINI_PACKAGE` tells the example's scripts where the package is:

   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   export CONFIGHUB_MINI_PACKAGE="$MINI"
   unset CUB_CONTEXT
   confighub-mini-app mini install-plugin "$CUB_CONFIG"
   ```

2. Copy the example into a folder of your own:

   <!-- run: copy files -->
   ```sh
   mkdir -p ~/walkthrough && cp -R "$MINI/examples/gpu-platform" ~/walkthrough/ && cd ~/walkthrough/gpu-platform
   ```

3. Render the platform, NVIDIA's GPU Operator, at its current and next versions:

   <!-- run: render files -->
   ```sh
   ./render
   ```

4. Play all three parties. `./two-people` gives each party a `cub` configuration and a hub of its own in a folder of its own, makes each key with `openssl` on the side of the person who will hold it, and tries every step a key should be refused. It keeps a copy of what it printed in `keys.txt`, and removes everything else it made at the end. It takes about a minute.

   <!-- run: keys -->
   ```sh
   ./two-people | tee keys.txt
   ```

   ```text
   …
   2. Ivan's team gives the customer a key that can only read the platform
   …
   The read key tries to change Ivan's platform: HTTP 403: permission denied
   …
   4. The customer gives Dan a key that can change their installation, and nothing else
   …
   Dan tries to change the customer's copy of the platform: HTTP 403: permission denied
   Dan tries to make a Space of his own there: HTTP 403: permission denied
   …
   Dan signs in again: Invalid credentials
   …
   And beside the values in the files:
   version: "580.95.05" # Customer: our nodes are certified with driver 580.95.05
   …
   you keep Driver version yours: "580.95.05" (offered: "580.126.20")
   …
   ```

5. Read what happened, in `keys.txt`:
   - The customer's key could read Ivan's platform and copy it into the customer's own hub, and was refused when it tried to change it.
   - Dan's key could change the customer's installation, with the customer's reasons, and was refused on the platform and when it tried to make anything new.
   - The customer removed Dan's key; his next sign-in was refused. The list of changes still says `by dan` beside each value he set.
   - Months later the customer took the platform's next version from Ivan's hub and kept the driver Dan recorded. Ivan's team never held a key to the customer's hub.

   <!-- run: keys-read -->
   ```sh
   grep -c 'HTTP 403: permission denied' keys.txt
   ```

   ```text
   3
   ```

### Undo it

`./two-people` already removed its hubs and keys. This removes the walkthrough's folder and `cub` configuration:

<!-- run: undo -->
```sh
cd ~ && rm -rf ~/walkthrough "$CUB_CONFIG"
```

### What you have now

Nothing left behind but the transcript. It is git's model, not a company sign-on system: on your own machine your key is who you are, others get keys you grant, limited to what they need, and nobody sends anyone a private key. The full story adds moving a hub's work up to the organization's shared ConfigHub, where the company's own sign-on comes in; [from your laptop to a shared hub](../../docs/from-plugin-to-confighub.md) covers that, and [agent keys](../../docs/agents-that-run-for-weeks.md#who-acted-give-the-agent-a-key-of-its-own) covers a key for an agent.

## Agent

For an AI agent doing this for a person.

- **The request:** "Show me that the customer, Dan and Ivan's team each only get their own part: run the three-party key check from the GPU platform example and tell me whether every refusal happened."
- **What to run:** the Human step 4, in a rendered copy of `$MINI/examples/gpu-platform`, keeping the output in `keys.txt`. Report each refusal, and any line that says `NOT REFUSED. That is a fault.`
- **Never:** copy, print or move a private key (`*.jwk` without `.pub`); grant a key more than its part needs; work around a refusal.
- **Done when:** `keys.txt` shows three `HTTP 403: permission denied` lines, `Invalid credentials` for Dan's removed key, and no `NOT REFUSED`.

## Testing

The scripted run follows the Human steps and compares the quoted output. Arm a, without confighub mini, is not applicable here: the keys and refusals exist only in a hub. A correct agent result is a `keys.txt` with every refusal and none missed. The checks below can be run by hand after the steps:

This proves: stored, and refused. Each key is checked against real hubs on this computer, three of them; nothing is delivered, and no shared hub is used. The next step this aims to win: moving from hubs on one computer to the organization's hosted ConfigHub.

<!-- agent-task: keys -->
> This folder's ./two-people is a check of keys for three parties: Ivan's team, a customer, and Dan. Run it, keep its output in keys.txt, and tell me whether each party was refused everything outside its own part.

<!-- agent-check keys: f=$(find . -name keys.txt | head -1) && [ "$(grep -c 'HTTP 403: permission denied' "$f")" -ge 3 ] && grep -q 'Dan signs in again: Invalid credentials' "$f" && ! grep -q 'NOT REFUSED' "$f" -->
<!-- agent-tools: ./two-people tee -->
<!-- arms: b -->
<!-- next-step when "recorded": move up to the organization's ConfigHub | Move these keys, and what each may change, up to your organization's hosted ConfigHub? -->

```sh
grep -E '403|Invalid credentials|NOT REFUSED' keys.txt
```
