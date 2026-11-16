# Why not just Git, your hosting service or a rules file

For anyone asking what ConfigHub replaces. [The front page](../README.md) tells the durable config story: why it is needed now, one setup becoming two apps, and how it differs from platform engineering. This page compares ConfigHub with the tools you already have, and shows one team using it across ten services.

## Why Git, your hosting service and a rules file are not enough

- **Git** keeps a diff once someone commits. It shows nothing for a change nobody committed. If all you want is a reason in each commit message, one line in `CLAUDE.md` asks for that. ConfigHub keeps the reason by value, across sessions, and tells the next agent before it undoes one ([limits](limits.md)).
- **Your hosting service's settings** keep the current value. They don't know what you asked your agent for, and an agent with your sign-in can change production there. ConfigHub sits beside your host: with Vercel or Fly, you try a setting in staging, and when you approve a production change the same command puts it live on the host ([Next.js on Vercel](nextjs-on-vercel.md)).
- **A rule in `CLAUDE.md`** that says "ask first" is only a request. An agent that holds the keys can be talked past it ([an agent that can propose and cannot approve](../examples/walkthroughs/story-11-propose-not-approve.md)).
- **Branch protection and CODEOWNERS** approve a commit, and they stay the gate when Argo CD or Flux deploys from Git. ConfigHub adds the reason for each value, and a pull-request check that names any value nobody approved ([an app Argo CD or Flux deploys](journeys/gitops-app.md)).

## One team, many apps, many agents

Priya's platform team looks after ten services, and coding agents change their configuration.

1. **One base for all ten.** The team keeps the settings every service shares in one base, and each service keeps the few values it sets itself. When the team changes the base once, every service takes the change, and no service's own values are touched ([one base for every service](../examples/walkthroughs/story-24-company-base.md)).
2. **Agents propose, and a person approves.** Each agent has a key of its own. It proposes Friday's change, it is refused when it tries to approve it, and production changes only when Priya says yes ([propose, not approve](../examples/walkthroughs/story-11-propose-not-approve.md)).
3. **A yes in Slack counts only when it is hers.** Priya is told in the thread where the work was asked for, and her Approve there records the approval as hers. An agent relaying "Priya said yes" approves nothing ([approve from Slack](../examples/walkthroughs/story-22-priya-slack.md)).
4. **What is running, and why.** For an app Argo CD deploys, the team sees Git, the hub and the cluster side by side, and sorts each difference into deliberate, drift, or Git out of date ([Git, the hub and what is running](../examples/walkthroughs/story-09-git-hub-and-running.md)).
