#!/usr/bin/env python3
"""
Send a home-network heartbeat to a cloud endpoint.

This script is intentionally small and beginner-friendly:

- It runs classify_outage.py.
- It sends the classification JSON to AWS over HTTPS.
- If sending fails, it writes the payload to a local queue file.
- On the next successful internet connection, it tries to flush queued payloads.

No email, Telegram, or SMS is sent by the Raspberry Pi. Cloud-side alerting is
handled by AWS if heartbeats stop arriving.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_QUEUE_FILE = Path("logs/heartbeat_queue.jsonl")
DEFAULT_SITE_ID = "home"


def run_classifier():
    """Run classify_outage.py and return its JSON summary."""
    script_path = Path(__file__).with_name("classify_outage.py")
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    marker = "JSON summary:"
    if marker not in completed.stdout:
        raise RuntimeError(f"classifier JSON marker not found: {completed.stdout}")

    json_text = completed.stdout.split(marker, 1)[1].strip()
    payload = json.loads(json_text)
    payload["classifier_exit_code"] = completed.returncode
    return payload


def post_json(url, token, payload, timeout_seconds):
    """POST JSON to the heartbeat endpoint."""
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "authorization": f"Bearer {token}",
            "content-type": "application/json",
            "user-agent": "home-network-sre-monitor/1.0",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        response_body = response.read().decode("utf-8")
        return response.status, response_body


def append_queue(queue_file, payload):
    """Append a failed heartbeat payload to the local queue."""
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    with queue_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_queue(queue_file):
    """Read queued heartbeat payloads from disk."""
    if not queue_file.exists():
        return []

    payloads = []
    with queue_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                payloads.append(json.loads(line))
    return payloads


def write_queue(queue_file, payloads):
    """Rewrite the queue with payloads that still need retry."""
    if not payloads:
        queue_file.unlink(missing_ok=True)
        return

    queue_file.parent.mkdir(parents=True, exist_ok=True)
    with queue_file.open("w", encoding="utf-8") as handle:
        for payload in payloads:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def send_payload(url, token, payload, timeout_seconds):
    """Send one payload and return True when successful."""
    try:
        status, response_body = post_json(url, token, payload, timeout_seconds)
        print(f"Heartbeat sent: HTTP {status} {response_body}")
        return 200 <= status < 300
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"Heartbeat send failed: {exc}")
        return False


def flush_queue(url, token, queue_file, timeout_seconds):
    """Try to send queued payloads. Keep anything that still fails."""
    queued = read_queue(queue_file)
    if not queued:
        return

    print(f"Queued payloads found: {len(queued)}")
    remaining = []

    for payload in queued:
        if not send_payload(url, token, payload, timeout_seconds):
            remaining.append(payload)

    write_queue(queue_file, remaining)
    print(f"Queued payloads remaining: {len(remaining)}")


def parse_args(argv):
    """Parse command-line arguments and environment fallback values."""
    parser = argparse.ArgumentParser(description="Send cloud heartbeat for home network monitor.")
    parser.add_argument("--url", default=os.getenv("HEARTBEAT_URL"), help="AWS heartbeat endpoint URL.")
    parser.add_argument("--token", default=os.getenv("HEARTBEAT_TOKEN"), help="Shared heartbeat bearer token.")
    parser.add_argument("--site-id", default=os.getenv("HEARTBEAT_SITE_ID", DEFAULT_SITE_ID))
    parser.add_argument("--queue-file", default=os.getenv("HEARTBEAT_QUEUE_FILE", str(DEFAULT_QUEUE_FILE)))
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser.parse_args(argv)


def main(argv):
    """Program entry point."""
    args = parse_args(argv)
    if not args.url or not args.token:
        print("Missing HEARTBEAT_URL or HEARTBEAT_TOKEN. Nothing sent.", file=sys.stderr)
        return 2

    queue_file = Path(args.queue_file)
    payload = run_classifier()
    payload["site_id"] = args.site_id
    payload["sent_at_epoch"] = int(time.time())

    # Send any older queued payloads before the latest heartbeat.
    flush_queue(args.url, args.token, queue_file, args.timeout)

    if send_payload(args.url, args.token, payload, args.timeout):
        return 0

    append_queue(queue_file, payload)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

