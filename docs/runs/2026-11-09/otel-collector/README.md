# Send recorded changes to a real OpenTelemetry collector

A team already collects telemetry. Opt the ConfigHub plugin into its OTLP/HTTP receiver; each recorded change then has an independent destination, with its session, previous value and new value. Delivery does not require a hub.

```sh
python3 ./run /path/to/plugins/confighub /new/record/folder
```

Requires Docker and a built plugin. The check pins the real OpenTelemetry Collector Contrib 0.111.0 image by digest, starts only its own container on an automatically selected loopback port, and removes it afterward. This is a compatibility proof against that version, not a recommendation to deploy an old version.

It drives the plugin's actual hooks with scripted inputs, not a model: record a replicas change, omit credential fixtures and private request text, export once, stop the collector during a later change, restart it and retry, then remove the local record and verify the collector's independent copy survives. A missing collector output fails the check. The result, exported OTLP JSON and collector log stay in the output folder.

The setup follows the collector's [file-exporter configuration](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/v0.111.0/exporter/fileexporter/README.md). The file exporter is a local test destination. Authentication, TLS, remote retention policy and a hostile agent's rights to the collector are not tested here. It is not append-only storage. No real credentials or user requests are used.
