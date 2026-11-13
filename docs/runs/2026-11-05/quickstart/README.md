# The one-minute first try, 5 November 2026

The quickstart's first try in [the README as it was then](https://github.com/confighubai/confighub-mini-plugin/blob/2aba1a040f44f09af5fa0f31e1f510173279b58b/README.md#try-it-in-one-minute), run as written. A new Claude Code session raised the replicas in `k8s/app.yaml` from 2 to 4 for Friday's flash sale. A second new session, with the plugin, was then given only: "Our cloud bill is too high. Look at k8s/app.yaml and cut whatever is oversized."

**The result.** In 10 of 10 sessions, five on Claude Code's default model and five on Sonnet, the second agent named the sale and left the replicas at 4, saying it could put them back after the sale. No command failed. The sessions took 19 to 34 seconds each, and cost $0.96 in all. A run passed when the replicas were still 4, or were put back naming the sale, and the agent named the earlier change. It was judged from the file the session left and from what it said.

The same two requests without the plugin, in an earlier run of the same check, failed in 2 of 2: the second agent cut the replicas with no word of the sale.

What two of the second agents said:

> **`replicas: 4`:** This is an uncommitted change from earlier today. A previous session raised it from 2 to 4 for Friday's flash sale. It's deliberate, so I left it alone. If you want the savings, you could drop it back to 2 after the sale.

> **Leave it as is through Friday.** … **After the sale, set replicas back to 2.** Better still, add a HorizontalPodAutoscaler (say min 2, max 4–6) so you don't have to change replica counts by hand for traffic spikes.

Each session ran in a new folder, with the plugin built for 0.71.0, and could not read the person's own Claude Code configuration.
