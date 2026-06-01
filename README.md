# home-network-sre-monitor

Beginner-friendly SRE portfolio project for monitoring a home network using a Raspberry Pi, Prometheus, Grafana, and simple local alerting.

This project is designed around a real home setup:

- ISP: ACT
- Router/mesh: TP-Link Deco
- Monitoring host: Raspberry Pi

Milestone 1 is intentionally only a repository scaffold. The goal is to document the shape of the system before adding real monitoring logic.

## Project Goals

- Monitor home internet and local network health.
- Classify outages in an SRE-style way.
- Build dashboards that show useful network reliability signals.
- Add alerting that still works locally when the internet is down.
- Write runbooks and tests that make the project resume-friendly.

## Important Constraints

- No secrets should be committed to this repository.
- Do not hardcode your public IP address.
- Use placeholder private IPs such as `192.168.68.1` until you configure your real local network.
- Cloud alerts cannot be sent during a full ACT internet outage unless there is backup internet.

## Planned Architecture

The Raspberry Pi will eventually run:

- Prometheus for metrics collection.
- Blackbox Exporter for probing local and internet endpoints.
- Grafana for dashboards.
- A small outage classifier script.
- Local-first alerting such as a buzzer, LED, local dashboard, or optional Google Home announcement.

## Milestone Status

Milestone 1 created:

- Initial documentation.
- Placeholder Docker Compose file.
- Placeholder Prometheus and Blackbox Exporter configs.
- Placeholder outage classification and health-check scripts.
- Screenshot folder for future dashboard images.

Milestone 2 adds the first runnable monitoring stack:

- Prometheus.
- Blackbox Exporter.
- Node Exporter.
- Grafana.

The stack is still basic and does not include external alerting yet.

Milestone 3 adds:

- A beginner-friendly outage classifier script.
- Human-readable status output.
- JSON output for future automation.
- Exit code `0` for `OK` and `1` for degraded/failure states.

## Outage Classifier

Run on the Raspberry Pi:

```sh
python3 scripts/classify_outage.py
```

Example healthy output:

```text
Status: OK
All checks passed. Home network looks healthy.

Checks:
- Gateway ping: OK, latency=5.1 ms
- Public IP ping 1.1.1.1: OK, latency=9.2 ms
- Public IP ping 8.8.8.8: OK, latency=14.4 ms
- DNS lookup: OK, latency=35.7 ms
- HTTPS request: OK, latency=220.5 ms

JSON summary:
{
  "classification": "OK",
  "...": "..."
}
```

Example degraded output:

```text
Status: DNS_FAILURE
Public IP checks work, but DNS lookup failed. This looks like a DNS issue.

Checks:
- Gateway ping: OK, latency=5.0 ms
- Public IP ping 1.1.1.1: OK, latency=9.0 ms
- Public IP ping 8.8.8.8: OK, latency=14.0 ms
- DNS lookup: FAIL, error=[Errno -2] Name or service not known
- HTTPS request: FAIL, error=<urlopen error ...>

JSON summary:
{
  "classification": "DNS_FAILURE",
  "...": "..."
}
```

## Next Milestones

1. Run Prometheus and Blackbox Exporter locally.
2. Add basic probes for router, DNS, and internet reachability.
3. Add Grafana dashboard screenshots.
4. Implement simple outage classification.
5. Add local alerting and runbooks.

## Repository Structure

```text
.
├── blackbox/
│   └── blackbox.yml
├── docs/
│   ├── alerting-limitations.md
│   ├── architecture.md
│   ├── failure-mode-test-plan.md
│   └── setup-guide.md
├── prometheus/
│   └── prometheus.yml
├── scripts/
│   ├── classify_outage.py
│   └── network_health_check.sh
├── screenshots/
│   └── .gitkeep
├── .env.example
├── docker-compose.yml
└── README.md
```
