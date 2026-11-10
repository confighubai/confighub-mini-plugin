#!/usr/bin/env python3
"""A small running app: its configured request limit is real HTTP behaviour."""
import http.server
import hashlib
import json
import os
import pathlib
import uuid

config = pathlib.Path(os.environ["APP_CONFIG"])
raw = config.read_bytes()
settings = dict(line.split("=", 1) for line in raw.decode().splitlines()
                if line and not line.startswith("#") and "=" in line)
receipt = json.loads((config.parent / ".cub-mini-pull.json").read_text())
pulled = receipt["files"][config.name]
if pulled["sha256"] != hashlib.sha256(raw).hexdigest() or pulled["revision"] < 1:
    raise SystemExit("The settings and pull receipt do not match; refusing to report an unverified revision")
if int(settings["MAX_BODY_BYTES"]) < 1 or settings["DEBUG"] not in ("true", "false"):
    raise SystemExit("Invalid request limit or debug setting")
configuration = dict(space=receipt["space"], unit=pulled["unit"], revision=pulled["revision"], sha256=pulled["sha256"])
instance = str(uuid.uuid4())

class API(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        data = json.dumps(dict(settings, instance=instance, configuration=configuration)).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > int(settings["MAX_BODY_BYTES"]):
            self.send_error(413, "Request exceeds this copy's configured limit")
            return
        self.rfile.read(length)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"accepted\n")

server = http.server.HTTPServer(("127.0.0.1", 0), API)
pathlib.Path(os.environ["APP_PORT_FILE"]).write_text(str(server.server_port))
server.serve_forever()
