# Architecture

This project monitors a home network from a Raspberry Pi.

## Current Milestone

Milestone 1 only creates the repository structure and placeholder files. The architecture below describes the intended direction, not a fully implemented system.

## High-Level Design

```text
Home devices
    |
TP-Link Deco router/mesh
    |
Raspberry Pi monitoring stack
    |
Prometheus + Blackbox Exporter + Grafana
    |
Local-first alerts and future cloud notifications
```

## Main Components

### Raspberry Pi

The Raspberry Pi is the monitoring host. It should stay powered on and connected to the home network.

### TP-Link Deco

The Deco router or mesh gateway is the main local network target. A placeholder IP such as `192.168.68.1` is used in examples. Replace it with the real local gateway IP during setup.

The current local network check found the active Wi-Fi subnet as `192.168.68.0/24` with Deco gateway and DHCP at `192.168.68.1`.

### Prometheus

Prometheus will collect probe results and time-series metrics.

### Blackbox Exporter

Blackbox Exporter will check whether important targets are reachable, such as:

- Router gateway.
- DNS resolver, currently Cloudflare Security DNS at `1.1.1.2` and `1.0.0.2`.
- Public internet endpoint.
- Optional local services.

### Grafana

Grafana will provide dashboards for latency, reachability, and outage history. Grafana is planned for a later milestone.

### Outage Classifier

The future classifier will compare local and internet checks to classify likely failure modes:

- Raspberry Pi issue.
- Local Wi-Fi or LAN issue.
- Router or Deco issue.
- DNS issue.
- ISP or ACT outage.
- Unknown or partial failure.

## Alerting Philosophy

Alerting should be local-first because internet outages can prevent cloud services from receiving alerts.

Local alert options:

- Raspberry Pi buzzer.
- Raspberry Pi LED.
- Local dashboard visible inside the home network.
- Optional Google Home announcement if it works on the local network.

Cloud alert options:

- Email, webhook, or chat notification after internet recovers.
- Backup internet path if available.

Cloud alerts cannot be relied on during a full ACT outage unless the Raspberry Pi has another internet path.
