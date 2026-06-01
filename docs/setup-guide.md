# Setup Guide

This guide is intentionally beginner-friendly. Milestone 2 runs the first basic monitoring stack on a Raspberry Pi.

## Prerequisites

You will need:

- Raspberry Pi connected to your home network.
- Docker installed on the Raspberry Pi.
- Docker Compose available.
- Git installed.

The target operating system is Raspberry Pi OS or another Debian-based Linux distribution.

## Configuration

1. Review `.env.example`.
2. Copy it to `.env` when you are ready to configure local values.
3. Replace placeholder values with your actual local settings.

Do not commit `.env`.

## Router IP

The current Windows CLI check detected:

- Active adapter: Wi-Fi
- Local IPv4 address: `192.168.68.100`
- Local subnet: `192.168.68.0/24`
- TP-Link Deco gateway: `192.168.68.1`
- DHCP server: `192.168.68.1`
- IPv4 DNS servers: `1.1.1.2`, `1.0.0.2`
- DNS over HTTPS endpoint: `https://security.cloudflare-dns.com/dns-query`

These are private/local network details and Cloudflare DNS details. Do not commit public IP addresses or secrets.

The examples use `192.168.68.1` as the TP-Link Deco gateway IP. Your real Deco gateway may be different if the network is reconfigured.

You can usually find it from:

- The Deco app.
- Your computer network settings.
- A command such as `ip route` on Linux.

On Windows, useful commands are:

```powershell
ipconfig /all
Get-NetIPConfiguration
Get-DnsClientServerAddress -AddressFamily IPv4
Get-NetRoute -AddressFamily IPv4
Get-DnsClientDohServerAddress
```

## Install Git On Raspberry Pi

On the Raspberry Pi:

```sh
sudo apt update
sudo apt install -y git curl ca-certificates
```

## Install Docker On Raspberry Pi

Use Docker's official convenience script for a beginner-friendly first setup:

```sh
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker "$USER"
```

Log out and log back in so your user can run Docker commands without `sudo`.

Check Docker:

```sh
docker --version
docker compose version
```

## Clone This Repository

Replace the URL with your GitHub repository URL after you push it:

```sh
git clone https://github.com/YOUR_USERNAME/home-network-sre-monitor.git
cd home-network-sre-monitor
```

If you copy the project to the Raspberry Pi manually instead of using GitHub, just `cd` into the project folder.

## Create Local Environment File

```sh
cp .env.example .env
nano .env
```

Review these values:

- `ROUTER_IP`
- `LOCAL_SUBNET`
- `PRIMARY_DNS`
- `SECONDARY_DNS`
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

Important: the current Prometheus probe targets are edited in `prometheus/prometheus.yml`. The `.env` file documents local values for scripts and future milestones.

## Run The Monitoring Stack

From the repository folder:

```sh
docker compose up -d
```

This starts:

- Prometheus on port `9090`.
- Grafana on port `3000`.
- Blackbox Exporter on port `9115`.
- Node Exporter on port `9100`.

## Check Container Status

```sh
docker compose ps
```

You can also view logs:

```sh
docker compose logs prometheus
docker compose logs blackbox
docker compose logs node-exporter
docker compose logs grafana
```

## Access Prometheus

From a browser on the same home network:

```text
http://RASPBERRY_PI_IP:9090
```

On the Raspberry Pi itself:

```text
http://localhost:9090
```

Useful Prometheus pages:

- `Status` > `Targets`
- `Graph`

Example queries:

```promql
up
probe_success
probe_duration_seconds
node_load1
```

The Prometheus labels are intentionally beginner-readable:

- Node Exporter appears as `raspberry-pi`, with `host="raspberry-pi"`.
- Blackbox Exporter appears as `blackbox-exporter`.
- Deco gateway probe appears as `deco-gateway`.
- DNS probes appear as `cloudflare-dns`, `google-dns`, `cloudflare-dns-lookup`, and `google-dns-lookup`.
- The original probe target is preserved in the `probed_target` label.

## Access Grafana

From a browser on the same home network:

```text
http://RASPBERRY_PI_IP:3000
```

On the Raspberry Pi itself:

```text
http://localhost:3000
```

Default local test login:

- Username: `admin`
- Password: `admin`, unless you changed `GRAFANA_ADMIN_PASSWORD` in `.env`

After logging in, add Prometheus as a Grafana data source:

```text
http://prometheus:9090
```

Milestone 2 also provisions this automatically:

- Data source: `Prometheus`
- Dashboard folder: `Home Network SRE`
- Dashboard: `Home Network SRE Overview`

If Grafana looks empty, go to `Dashboards` and open the `Home Network SRE` folder.

## Current Probe Targets

Prometheus currently runs Blackbox Exporter checks for:

- Deco gateway placeholder: `192.168.68.1`
- Cloudflare DNS IP: `1.1.1.1`
- Google DNS IP: `8.8.8.8`
- HTTPS check: `https://www.google.com`
- DNS lookup check: `google.com`

Edit `prometheus/prometheus.yml` if your Deco gateway is different.

## Run The Outage Classifier

Milestone 3 adds a local outage classification script. It uses only the Python standard library, so no `pip install` step is required.

Run it on the Raspberry Pi from the repository folder:

```sh
python3 scripts/classify_outage.py
```

Run it with explicit values:

```sh
python3 scripts/classify_outage.py \
  --gateway 192.168.68.1 \
  --public-target 1.1.1.1 \
  --public-target 8.8.8.8 \
  --dns-domain google.com \
  --https-url https://www.google.com \
  --latency-threshold-ms 150
```

The script exits with:

- `0` when the classification is `OK`.
- `1` when the network is degraded or failed.

The latency rule uses successful ping measurements from the gateway and public IP targets.

Useful test commands:

```sh
python3 scripts/classify_outage.py --latency-threshold-ms 1
python3 scripts/classify_outage.py --gateway 192.168.68.254
python3 scripts/classify_outage.py --dns-domain definitely-not-a-real-domain.invalid
```

## Beginner Notes

- Prometheus stores measurements over time.
- Blackbox Exporter tests whether targets are reachable.
- Grafana turns metrics into dashboards.
- Alerts should include local options because cloud notifications may fail during an ISP outage.
- Milestone 2 does not configure Telegram, email, cloud alerts, or Home Assistant.
