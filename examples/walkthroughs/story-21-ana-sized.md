<!-- walkthrough
id: story-21-ana-sized
starts_with: mini
story: "21. Ana's service, sized by what it used"
needs: [cub mini package, Docker, Python 3]
budget_seconds: 240
-->
# A new service sized by what it used, with the measurement as the reason

Ana's agent built a small notes service on her team's pattern, which gives every service 2 CPU and 4Gi of memory. Nobody has seen it run, so nobody knows whether that is ten times too much or too little. Here the service runs in a container on your computer while a load generator sends it a stated number of requests, and what it used becomes the proposed size: each size an ordinary setting whose reason is the measurement. Staging takes it at once; production waits for Sam, who looks after the team's hub, to read the numbers and approve.

## Human

For a person following along in a terminal.

### What you need

An unpacked confighub mini package (from the [releases page](https://github.com/confighubai/confighub-mini-plugin/releases)) on macOS or Linux, Docker running, and Python 3. confighub mini is a hub, a small ConfigHub server that keeps each setting with who changed it and why, running on your computer only. No account and no cluster.

### Steps

1. Set up a terminal. `MINI` is the unpacked package; `CUB_CONFIG` is a new folder for this walkthrough's `cub` settings, so nothing of yours is touched. Then start a hub:
   <!-- run: setup -->
   ```sh
   export MINI=/absolute/path/to/unpacked-confighub-mini
   export PATH="$MINI/bin:$PATH"
   export CUB_CONFIG="$HOME/.confighub-walkthrough"
   unset CUB_CONTEXT
   "$MINI/bin/confighub-mini-app" mini install-plugin "$CUB_CONFIG" >/dev/null
   cub mini install --name ana --use --arrival no >/dev/null
   ```

2. Ana's service, as her agent wrote it: a small HTTP API with a `Dockerfile`, and its settings in `app.env`, with the pattern's sizes. At start it builds a search index, which takes more memory than it keeps:
   <!-- run: app files -->
   ```sh
   mkdir -p ~/walkthrough && cd ~/walkthrough
   cp -R /absolute/path/to/unpacked-confighub-mini/examples/sized/notes notes
   grep -E '^(CPU|MEMORY)=' notes/app.env
   ```
   ```text
   CPU=2
   MEMORY=4Gi
   ```

3. Give its settings to the hub: a base, a staging copy and a production copy, `notes-live`. Sam approves production's starting values and gives Ana's agent a key of its own, which can change staging and only ask for production:
   <!-- run: adopt -->
   ```sh
   cub mini adopt notes >/dev/null
   cub mini approve notes-base/adopt --note "What runs today" --yes >/dev/null
   cub mini require-approval notes --variant live --agent bot >/dev/null
   cub unit data --space notes-live app | grep -E '^(CPU|MEMORY)='
   ```
   ```text
   CPU=2
   MEMORY=4Gi
   ```

4. Measure it. `measure` builds the service, runs it in a container with its current sizes as the container's limits, as Kubernetes would, and sends it 20 requests a second for 20 seconds. Docker's own `docker stats` reads its CPU and memory about twice a second, and the kernel's record of the peak catches anything shorter:
   <!-- run: measure -->
   ```sh
   "$MINI/examples/sized/measure" notes --rate 20 --seconds 20
   ```
   ```text
   Measured notes in a container with its current sizes as limits (CPU=2, MEMORY=4Gi), read by docker stats:
   …
     Listens on: 8080.
     Load: 20 requests a second for 20 seconds, GET /: 400 answered, 0 failed.
   …
   Wrote notes.measured.json. To propose sizes from it: propose notes notes.measured.json
   ```
   The lines left out say how long the service took to answer, and the most CPU and memory it used, which differ a little from run to run.

5. The agent proposes sizes from the measurement, on its own key. The rule is plain: CPU is the most it used under that load plus a quarter, rounded up to the next 50m; memory is the most it used, start included, plus a half, rounded up to the next 64Mi. `propose` writes them into `app.env` and hands the change to the hub with `cub mini upload`, the ordinary way a change to the app's files reaches it:
   <!-- run: size -->
   ```sh
   CUB_CONTEXT=bot "$MINI/examples/sized/propose" notes notes.measured.json
   ```
   ```text
   Proposed for notes, from notes.measured.json:
   …
   Production keeps its current settings until you approve this change. To see the change and approve it:
   …
   ```
   The reason it gives the hub names what the sizes were, the load, what the service used, the sizes proposed and the rule: "Sized from what it used: it had CPU=2 and MEMORY=4Gi; in the sandbox, at 20 requests a second for 20 seconds, it used at most … CPU and, start included, …Mi; proposed CPU=… and MEMORY=…"

6. Sam reads what waits for production: the sizes, with the measurement as the reason. Staging has them already:
   <!-- run: waiting -->
   ```sh
   cub mini waiting
   ```
   ```text
   …
     It proposes for production, from the app's files:
   …
   ```

7. Sam approves, and production has the measured sizes. The receipt keeps who approved and why each size is what it is:
   <!-- run: approve -->
   ```sh
   cub mini approve notes-live --note "Sized from what it used" --yes >/dev/null
   test "$(cub unit data --space notes-live app | grep -E '^(CPU|MEMORY)=')" = "$(grep -E '^(CPU|MEMORY)=' notes/app.env)" && echo "Production has the measured sizes."
   cub mini receipts notes-live | grep -m1 -o "Why: *Sized from what it used"
   ```
   ```text
   Production has the measured sizes.
   Why: Sized from what it used
   ```

8. A service that never answers gets no size. Here a copy whose container starts and never listens:
   <!-- run: never may-fail -->
   ```sh
   cp -R notes silent && printf 'FROM python:3.12-alpine\nCMD ["sleep", "600"]\n' > silent/Dockerfile
   "$MINI/examples/sized/measure" silent --seconds 5 --start-seconds 10
   ```
   ```text
   …
     It never answered on port 8080 within 10 seconds.
   No size can come from this run: the service never answered, so nothing it did can be measured. Wrote silent.measured.json.
   ```
   `propose` refuses that file too, and so it does a run in which the service was killed, or failed more than 1 request in 100.

### Undo it

`cub mini uninstall --name ana --delete-data` removes the hub and everything in it; `docker image prune -af --filter label=confighub.sized` removes the images `measure` built, which it labels; then delete `~/walkthrough` and `~/.confighub-walkthrough`. `measure` removes each container it starts.

### What you have now

The notes service with sizes that come from what it did, each with its measurement and the load it was measured at as the reason, in staging at once and in production once Sam approved. A copy whose size someone kept, with their reason, keeps it: the proposal says what the measurement found there and changes nothing.

The sandbox's load is not production's, so every size says the load it was measured at. Once the service runs on a cluster, `"$MINI/examples/sized/from-live"` reads what it uses there from metrics-server, and `propose` takes that back the same way, with live's numbers as the reason and Sam's approval before production changes; a window on live has no start in it, so live may raise memory and never lowers it. The full story, and the example's `live` script on a local kind cluster, show it.

## Agent

For an AI agent doing this for a person.

- The request: "Our notes service has the pattern's 2 CPU and 4Gi. Size it by what it actually uses at 20 requests a second, with what you measured as the reason. Staging can take it now; production waits for Sam."
- Work with the key you were given: run `cub` as `cub --context bot`, and the two tools with `CUB_CONTEXT=bot`. Measure first: `"$MINI/examples/sized/measure" notes --rate 20 --seconds 20`. Then `CUB_CONTEXT=bot "$MINI/examples/sized/propose" notes notes.measured.json`.
- Do not write sizes you have not measured, and do not raise them "to be safe": the rule's headroom is in `propose`. If `measure` says no size can come from the run, tell the person why and propose nothing.
- Never approve a change for production, sign in as the person, or write `notes-live` directly.
- Done when `cub unit data --space notes-staging app` shows the proposed `CPU` and `MEMORY`, `cub unit data --space notes-live app` still shows `CPU=2` and `MEMORY=4Gi`, and `cub mini waiting` shows the change with the measurement. Tell the person the sizes, the measurement, and that production waits for Sam.

## Testing

This proves: the sizes were measured from the service running in a container, at a stated load, and stored in the hub as ordinary settings with the measurement as their reason, staging's at once and production's held for approval. What was really used: Docker on this computer, with `docker stats` and the kernel's peak, and confighub mini; no cluster, and the approval was made by the scripted steps, not a person. The load is a generator's, not production's. The step it aims to win: sizes from live, the story's last step.

The scripted run follows the Human steps on a hub of its own and checks that each quoted line is still printed. A correct agent result gives staging a CPU between 100m and 1 and a memory between 300Mi and 1Gi, which the service's start needs, keeps production at 2 and 4Gi, and keeps the measurement as the reason. In plain files: a staging file has the sizes, the shared `app.env` keeps 2 and 4Gi, and a file says what was measured. The checks below hold right after step 5, before Sam approves.

<!-- agent-task: size after=measure -->
> Our notes service has the pattern's 2 CPU and 4Gi. Size it by what it actually uses at 20 requests a second, with what you measured as the reason. Staging can take it now; production waits for Sam.

<!-- agent-check size: cub unit data --space notes-staging app | python3 -c 'import re,sys; d=dict(l.split("=",1) for l in sys.stdin.read().split() if "=" in l); n,u=re.fullmatch(r"([0-9.]+)(Mi|Gi)",d["MEMORY"]).groups(); c=d["CPU"]; c=float(c[:-1])/1000 if c.endswith("m") else float(c); sys.exit(not (300<=float(n)*(1024 if u=="Gi" else 1)<=1024 and 0.1<=c<=1))' && cub unit data --space notes-live app | grep -qx 'CPU=2' && cub unit data --space notes-live app | grep -qx 'MEMORY=4Gi' && cub mini receipts notes-staging | grep -qiE 'Why:.*(measur|used).*[0-9]+ ?Mi' -->
<!-- agent-check-a size: grep -qx 'CPU=2' notes/app.env && grep -qx 'MEMORY=4Gi' notes/app.env && f=$(grep -rlsE '^ *"?MEMORY"? *[=:] *"?[0-9]+(Mi|M|MiB)' --exclude-dir='.*' --exclude-dir=Library . | grep -i staging | head -1) && test -n "$f" && grep -rlsiE '(measur|used|peak).*[0-9]+ ?(Mi|MiB|MB)' --exclude-dir='.*' --exclude-dir=Library . | grep -qv server.py -->
<!-- arms: a,b -->
<!-- next-step boundary=same-tier: sizes from live | Once notes runs, what it uses there can come back as a proposed size the same way, with live's numbers as the reason and Sam's approval before it changes; want that for notes? -->

The checks below can be run by hand, in bash, in `~/walkthrough`:

```sh
cub unit data --space notes-staging app | grep -E '^(CPU|MEMORY)='; cub unit data --space notes-live app | grep -E '^(CPU|MEMORY)='
cub mini receipts notes-staging | grep 'Why:'
```

<!-- results:begin -->
<!-- results:end -->
