# Why durable config, and why now

For anyone deciding whether ConfigHub is worth a look, who wants the reasoning before the commands. [The front page](../README.md) shows what it does. This page says why it is needed now, shows one setup becoming two apps, and compares it with platform engineering as most teams know it.

## Why now

1. **People make and run apps by asking agents.** An agent changes settings many times a day, across staging, production and every customer's copy. No one reads diffs that fast.
2. **So the platform has to come from somewhere else.** Staging, production, promotion, rollback and limits used to come from a platform team or a hosting service. An agent can now write them with the app. But they land in scattered files, the next session overwrites them, and every new app starts from nothing.
3. **ConfigHub keeps the setup, its changes and their context.** It keeps the setup itself, wherever the app runs, with every change to it and the context for each change: what was asked, and why. That is what durable means. What you and your agents decided is still there for:
   - **the next session**, which starts from what was set and why
   - **the next agent**, which is told before it undoes a value
   - **the next version**, which keeps your own values
   - **the next environment**, which takes exactly what you approved
   - **the next app**, which starts from the first

## An example: two apps from one setup

A developer builds a web shop with an agent. Their next app is a cart service.

1. **The first app gets a setup.** `cub mini adopt shop` gives the shop a staging and a production copy, with the team's settings from a [starter](starters.md), a small YAML file. Each setting has its reason.
2. **A fix to the first app becomes part of the setup.** A teammate proposes warning-level logs and three instances for the next starter version, with a reason for each setting. The owner approves the version.
3. **The second app starts with the fix, and the first keeps its own values.** The cart service starts with the new settings. The shop takes the update and keeps its production log level. Production changes still go through their own approval.

The walkthrough [Alice ships it, Bob hardens it](../examples/walkthroughs/story-25-alice-bob-hardened.md) runs this on your laptop.

## How this differs from platform engineering

Platform engineering builds a platform and fits apps to it. Durable config starts with the app, so the platform grows out of the apps.

| | Platform engineering as we know it | Durable config |
|---|---|---|
| What comes first | The platform, built by a team ahead of the apps | The app. Its setup becomes the base for the next one |
| How an app gets its setup | A template, copied once when the app is created | A starter the app stays linked to |
| Where the knowledge lives | Docs, tickets and the platform team's heads | With each value, as its reason |
| Who it is built for | People: portals, forms and golden-path guides | Agents and people |
| How a change spreads | One pull request in each repository | One change, read across every app |
| Where you can start | With a platform team | With one app on your computer |

ConfigHub doesn't run your app. Your cluster, hosting service or VM still does, and Argo CD and Flux still deliver to your clusters. It replaces the templates, the portal and the scattered settings files above them.
