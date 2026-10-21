# Configuration review

On each pull request, a comment with every configuration value the pull request changes, from what to what, and why, where the record the minihub plugin keeps of what agents change says. A value no record explains is shown as such. It reads Kubernetes files, Helm values, Kustomize, Compose, GitHub Actions workflows, settings files, Terraform variables and agent configuration. No hub, no account, nothing leaves the runner but the comment.

```yaml
name: Configuration review
on: pull_request
permissions:
  contents: read
  pull-requests: write
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: confighubai/minihub-plugin/review@v0
```

`@v0` follows every 0.x release; `@v0.38.0` stays on one.

The "why" comes from the records agents with the plugin keep in the repository (`CUB_MINI_RECORD_IN_REPO=1`). Without them, the review still lists each value changed.
