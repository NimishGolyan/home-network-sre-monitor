#!/usr/bin/env python3
"""
Beginner-friendly outage classifier for home-network-sre-monitor.

The script runs a few simple checks from the machine it is executed on:

- Ping the Deco gateway.
- Ping public IP targets.
- Resolve a DNS name.
- Fetch an HTTPS URL.
- Compare measured latency with a threshold.

It prints a human-readable summary first, then a JSON summary for automation.
No alerts are sent in this milestone.
"""

import argparse
import json
import platform
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone


DEFAULT_GATEWAY = "192.168.68.1"
DEFAULT_PUBLIC_TARGETS = ["1.1.1.1", "8.8.8.8"]
DEFAULT_DNS_DOMAIN = "google.com"
DEFAULT_HTTPS_URL = "https://www.google.com"
DEFAULT_LATENCY_THRESHOLD_MS = 150.0
DEFAULT_TIMEOUT_SECONDS = 3.0


def now_utc_iso():
    """Return an ISO-8601 timestamp for the JSON summary."""
    return datetime.now(timezone.utc).isoformat()


def build_ping_command(target, timeout_seconds):
    """Build a one-packet ping command for Windows or Linux."""
    system_name = platform.system().lower()

    if system_name == "windows":
        timeout_ms = int(timeout_seconds * 1000)
        return ["ping", "-n", "1", "-w", str(timeout_ms), target]

    # Raspberry Pi OS and Debian use this ping syntax.
    return ["ping", "-c", "1", "-W", str(int(timeout_seconds)), target]


def ping_target(target, timeout_seconds):
    """
    Ping a target once.

    The elapsed time is measured around the ping command so the script stays
    simple and does not need OS-specific ping output parsing.
    """
    command = build_ping_command(target, timeout_seconds)
    started = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 2,
            check=False,
        )
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "target": target,
            "ok": completed.returncode == 0,
            "latency_ms": round(elapsed_ms, 2) if completed.returncode == 0 else None,
            "error": None if completed.returncode == 0 else "ping failed",
        }
    except FileNotFoundError:
        return {
            "target": target,
            "ok": False,
            "latency_ms": None,
            "error": "ping command not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "target": target,
            "ok": False,
            "latency_ms": None,
            "error": "ping timed out",
        }


def dns_lookup(domain, timeout_seconds):
    """Resolve a DNS name using the system resolver."""
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout_seconds)
    started = time.perf_counter()

    try:
        addresses = sorted(set(socket.gethostbyname_ex(domain)[2]))
        elapsed_ms = (time.perf_counter() - started) * 1000
        return {
            "domain": domain,
            "ok": True,
            "latency_ms": round(elapsed_ms, 2),
            "addresses": addresses,
            "error": None,
        }
    except OSError as exc:
        return {
            "domain": domain,
            "ok": False,
            "latency_ms": None,
            "addresses": [],
            "error": str(exc),
        }
    finally:
        socket.setdefaulttimeout(old_timeout)


def https_request(url, timeout_seconds):
    """Make a small HTTPS request and record whether it succeeds."""
    started = time.perf_counter()
    request = urllib.request.Request(url, headers={"User-Agent": "home-network-sre-monitor/1.0"})

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            # Read a small amount so the connection is actually used.
            response.read(256)
            elapsed_ms = (time.perf_counter() - started) * 1000
            status_code = response.getcode()
            return {
                "url": url,
                "ok": 200 <= status_code < 400,
                "status_code": status_code,
                "latency_ms": round(elapsed_ms, 2),
                "error": None,
            }
    except Exception as exc:
        return {
            "url": url,
            "ok": False,
            "status_code": None,
            "latency_ms": None,
            "error": str(exc),
        }


def highest_latency_ms(*checks):
    """Return the highest successful latency from the provided check results."""
    latencies = []
    for check in checks:
        if isinstance(check, list):
            latencies.extend(item["latency_ms"] for item in check if item.get("latency_ms") is not None)
        elif check.get("latency_ms") is not None:
            latencies.append(check["latency_ms"])

    return max(latencies) if latencies else None


def highest_ping_latency_ms(gateway_ping, public_ip_pings):
    """Return the highest successful ICMP latency measurement."""
    return highest_latency_ms(gateway_ping, public_ip_pings)


def classify(results, latency_threshold_ms):
    """Apply simple classification rules in priority order."""
    gateway_ok = results["gateway_ping"]["ok"]
    public_ip_ok = any(item["ok"] for item in results["public_ip_pings"])
    dns_ok = results["dns_lookup"]["ok"]
    https_ok = results["https_request"]["ok"]
    max_latency = results["max_ping_latency_ms"]

    if not gateway_ok:
        return "DECO_GATEWAY_DOWN"

    if gateway_ok and not public_ip_ok and not https_ok:
        return "ACT_OUTAGE"

    if public_ip_ok and not dns_ok:
        return "DNS_FAILURE"

    if max_latency is not None and max_latency > latency_threshold_ms:
        return "HIGH_LATENCY"

    if gateway_ok and public_ip_ok and dns_ok and https_ok:
        return "OK"

    return "DEGRADED"


def status_message(classification):
    """Return a short explanation for humans."""
    messages = {
        "OK": "All checks passed. Home network looks healthy.",
        "DECO_GATEWAY_DOWN": "Deco gateway is unreachable. Check router power, Wi-Fi, or LAN connectivity.",
        "ACT_OUTAGE": "Gateway is reachable, but public internet checks failed. This looks like an ISP/WAN outage.",
        "DNS_FAILURE": "Public IP checks work, but DNS lookup failed. This looks like a DNS issue.",
        "HIGH_LATENCY": "Checks work, but latency is above the configured threshold.",
        "DEGRADED": "Some checks failed, but they do not match a specific outage rule yet.",
    }
    return messages.get(classification, "Unknown status.")


def run_checks(args):
    """Run all checks and return a structured result dictionary."""
    gateway_ping = ping_target(args.gateway, args.timeout)
    public_ip_pings = [ping_target(target, args.timeout) for target in args.public_targets]
    dns_result = dns_lookup(args.dns_domain, args.timeout)
    https_result = https_request(args.https_url, args.timeout)
    max_ping_latency = highest_ping_latency_ms(gateway_ping, public_ip_pings)

    results = {
        "timestamp": now_utc_iso(),
        "classification": None,
        "latency_threshold_ms": args.latency_threshold_ms,
        "max_ping_latency_ms": max_ping_latency,
        "gateway_ping": gateway_ping,
        "public_ip_pings": public_ip_pings,
        "dns_lookup": dns_result,
        "https_request": https_result,
    }
    results["classification"] = classify(results, args.latency_threshold_ms)
    return results


def print_human_summary(results):
    """Print a readable summary before the JSON output."""
    classification = results["classification"]

    print(f"Status: {classification}")
    print(status_message(classification))
    print()
    print("Checks:")
    print(format_check("Gateway ping", results["gateway_ping"]))

    for ping_result in results["public_ip_pings"]:
        print(format_check(f"Public IP ping {ping_result['target']}", ping_result))

    print(format_check("DNS lookup", results["dns_lookup"]))
    print(format_check("HTTPS request", results["https_request"]))
    print()
    print("JSON summary:")


def format_check(name, check):
    """Format one check as a compact human-readable line."""
    state = "OK" if check["ok"] else "FAIL"
    latency = check.get("latency_ms")
    latency_text = f", latency={latency} ms" if latency is not None else ""
    error = check.get("error")
    error_text = f", error={error}" if error else ""
    return f"- {name}: {state}{latency_text}{error_text}"


def parse_args(argv):
    """Parse CLI arguments and keep defaults easy to discover."""
    parser = argparse.ArgumentParser(description="Classify home network outage status.")
    parser.add_argument("--gateway", default=DEFAULT_GATEWAY, help="Gateway IP to ping.")
    parser.add_argument(
        "--public-target",
        dest="public_targets",
        action="append",
        default=None,
        help="Public IP to ping. Can be provided more than once.",
    )
    parser.add_argument("--dns-domain", default=DEFAULT_DNS_DOMAIN, help="Domain name for DNS lookup.")
    parser.add_argument("--https-url", default=DEFAULT_HTTPS_URL, help="HTTPS URL to request.")
    parser.add_argument(
        "--latency-threshold-ms",
        type=float,
        default=DEFAULT_LATENCY_THRESHOLD_MS,
        help="Classify HIGH_LATENCY above this latency in milliseconds.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Timeout per check in seconds.",
    )

    args = parser.parse_args(argv)
    if args.public_targets is None:
        args.public_targets = DEFAULT_PUBLIC_TARGETS
    return args


def main(argv):
    """Program entry point."""
    args = parse_args(argv)
    results = run_checks(args)
    print_human_summary(results)
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0 if results["classification"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
